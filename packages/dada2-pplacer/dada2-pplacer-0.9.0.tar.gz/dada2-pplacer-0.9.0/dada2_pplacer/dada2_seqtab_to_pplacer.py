#!/usr/bin/env python
import pandas as pd
import csv
import argparse
import sys
import logging
from multiprocessing import Pool

logging.basicConfig(format='DADA-pplacer-mothur:%(levelname)s:%(asctime)s:%(message)s', level=logging.INFO)

def lookup_sv_counts(spec_sv_tup):
    spec_idx, ordered_sv_idx, seqtab_T = spec_sv_tup
    return pd.arrays.SparseArray(
        [seqtab_T.iat[sv_idx, spec_idx] for sv_idx in ordered_sv_idx]
    )

def main():
    args_parser = argparse.ArgumentParser(description="""A small utility to convert dada2 style
    seqtables to a MOTHUR style sharetable and/or pplacer-style map and weights files.
    """)

    args_parser.add_argument('--seqtable', '-s',
                             help="Sequence table from dada2, in CSV format",
                             required=True, type=argparse.FileType('r'))
    args_parser.add_argument('--fasta_out_sequences', '-f',
                             help="Write sequence variants to this file, in FASTA format",
                             type=argparse.FileType('w'))
    args_parser.add_argument('--map', '-m',
                             help="Write pplacer-style mapping of sv to specimen",
                             type=argparse.FileType('w'))
    args_parser.add_argument('--weights', '-w',
                             help="Write pplacer-style weights of sv by specimen",
                             type=argparse.FileType('w'))
    args_parser.add_argument('--long', '-L',
                             help="Write out specimen, sv_id, count in long format",
                             type=argparse.FileType('w'))                             
    args_parser.add_argument('--sharetable', '-t',
                             help="Write mothur-style sharetable to this location",
                             type=argparse.FileType('w'))
    args_parser.add_argument('--cpus', '-C',
                             help="Number of threads to use. Default is number of vCPU available",
                             type=int, default=None)

    args = args_parser.parse_args()

    # Check to see if we've been tasked with anything. If not, we have nothing to do and should exit
    if not (args.fasta_out_sequences or args.map or args.weights or args.sharetable or args.long):
        sys.exit("Nothing to do")

    # Just convert our handles over to something nicer
    if args.fasta_out_sequences:
        out_sv_seqs_h = args.fasta_out_sequences
    else:
        out_sv_seqs_h = None
    if args.map:
        out_map_h = args.map
        map_writer = csv.writer(out_map_h)
    else:
        map_writer = None
    if args.weights:
        out_weights_h = args.weights
        weights_writer = csv.writer(out_weights_h)
    else:
        weights_writer = None
    if args.long:
        long_writer = csv.writer(args.long)
        # Header
        long_writer.writerow(['specimen', 'sv', 'count'])
    else:
        long_writer = None
    if args.sharetable:
        sharetable_fn = args.sharetable
    else:
        sharetable_fn = None
    logging.info("Loading DADA2 seqtable")
    # Load the sequence table

    # Reduce memory use by streaming in and using sparse structures
    seqtab_T = pd.DataFrame()

    seqtab_reader = csv.reader(args.seqtable)
    # Get the header, which are the SV sequences themselves
    sv_header = next(seqtab_reader)[1:]
    for r in seqtab_reader:
        specimen = r[0]
        counts = [int(c) for c in r[1:]]
        seqtab_T[specimen] = pd.arrays.SparseArray(
            counts,
            dtype=int,
            fill_value=0
        )
    logging.info("DADA2 Seqtable loaded")
    # Order the SV via their mean relative abundance\
    logging.info("Ordering SV by mean relative abundance")
    ordered_sv_idx = list((seqtab_T / seqtab_T.sum(axis=0)).mean(axis=1).sort_values(ascending=False).index)

    # Generate sv labels for each sequence variant,
    # and generate a dictionary to map sv_id to sequence-variant
    logging.info("Generating SV names")
    seq_idx_to_sv_num = {idx: 'sv-%d' % (i + 1) for i, idx in enumerate(ordered_sv_idx)}
    # Transpose, Reorder and Rename into a new seqtab
    logging.info("Generating new seqtable")
    convert_pool = Pool(args.cpus)
    num_specimens = len(seqtab_T.columns)
    seqtab_reorder = pd.DataFrame(
        convert_pool.imap(
            lookup_sv_counts,
            zip(
                range(num_specimens),
                [ordered_sv_idx] * num_specimens,
                [seqtab_T] * num_specimens
            )
        ),
        columns=[seq_idx_to_sv_num[sv_idx] for sv_idx in ordered_sv_idx],
        index=seqtab_T.columns
    )
    logging.info("Reordered seqtable done")

    # Annoyingly, we need to pick a representitive actual sequence
    # from each sv to be it's champion for guppy.
    # To do so, we will go through each column, find the max count for that sv,
    # and use that specimen as the champion
    logging.info("Finding maximum specimen for each SV")
    max_spec_for_sv = {sv_id: spec for sv_id, spec in seqtab_reorder.apply(lambda c: c.idxmax()).items()}

    if out_sv_seqs_h is not None:
        # Write out the sequences in fasta format, using the sv-id's generated above as an ID
        logging.info("Writing out SV to FASTA")
        for sv_idx in ordered_sv_idx:
            out_sv_seqs_h.write(">%s:%s\n%s\n" % (
                seq_idx_to_sv_num[sv_idx],
                max_spec_for_sv[seq_idx_to_sv_num[sv_idx]],
                sv_header[sv_idx]
            ))

    # Now write the mapping and weights files
    # Both are headerless CSV format files
    # map: sequence_id (sv_id:specimen), specimen
    # weight: sequence_id (sv_id here), specimen_sequence_id (sv_id:specimen here), count
    # This is a bit of a clunky structure (relating to some historic cruft)

    if map_writer or weights_writer or long_writer:
        logging.info("Writing out long, map, and/or weights")
        for spec, row in seqtab_reorder.iterrows():
            row_nonzero = row[row > 0]
            for sv_id, count in row_nonzero.items():
                if map_writer is not None:
                    map_writer.writerow([str(sv_id) + ":" + str(spec), spec])
                if weights_writer is not None:
                    weights_writer.writerow([
                        sv_id + ":" + max_spec_for_sv[sv_id],
                        str(sv_id) + ":" + str(spec),
                        count])
                if long_writer is not None:
                    long_writer.writerow([
                        spec,
                        sv_id + ":" + max_spec_for_sv[sv_id],
                        count
                    ])

    if sharetable_fn is not None:
        sharetable_labels = pd.DataFrame()
        sharetable_labels['label'] = list(seqtab_reorder.index)
        sharetable_labels['group'] = "dada2"
        sharetable_labels['numsvs'] = len(seqtab_reorder.columns)
        sharetable_labels.head()
        pd.merge(
            sharetable_labels,
            seqtab_reorder,
            left_on='label',
            right_index=True
        ).to_csv(sharetable_fn, index=False, sep='\t')        

    # Cleanup.
    if out_sv_seqs_h:
        out_sv_seqs_h.close()
    if map_writer:
        out_map_h.close()
    if weights_writer:
        out_weights_h.close()

# Boilerplate method to run this as a script
if __name__ == '__main__':
    main()
