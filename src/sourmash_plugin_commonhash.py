"""\
filter hashes by min occurrence across sketches

Reduce 'noise' in Jaccard comparisons of sequencing data by removing
hashes that are present in only a few sketches.

'commonhash' supports the full range of sourmash sketch output formats [1].

[1] https://sourmash.readthedocs.io/en/latest/command-line.html#choosing-signature-output-formats

---
"""

usage="""
   sourmash scripts commonhash [ -m 2 ] *.sig.gz -o filtered.zip
"""

epilog="""
See https://github.com/ctb/sourmash_plugin_commonhash for more examples.

Need help? Have questions? Ask at http://github.com/sourmash/issues!
"""

# For improvement CTB:
# * support full range of moltypes
# * support max samples, too

import argparse
import sourmash
from sourmash import sourmash_args, plugins
from collections import Counter

###

#
# CLI plugin - supports 'sourmash scripts commonhash'
#

class Command_CommonHash(plugins.CommandLinePlugin):
    command = 'commonhash'
    description = __doc__
    usage = usage
    epilog = epilog
    formatter_class = argparse.RawTextHelpFormatter

    def __init__(self, p):
        super().__init__(p)
        p.add_argument('sigfiles', nargs='+', help='input signatures')
        p.add_argument('-k', '--ksize', default=31, type=int,
                       help='select this k-mer size')
        p.add_argument('-o', '--output', required=True,
                       help="save sketches to this location; e.g. output.zip or ./output/")
        p.add_argument('-m', '--min-samples', default=2, type=int,
                       help="a hash must be in this many samples to be retained")

    def main(self, args):
        super().main(args)
        return do_commonhash(args)


def do_commonhash(args):

    print(f"Selecting k={args.ksize}, DNA")

    # first pass: count number of samples for each hash
    all_hashes = Counter()
    n_signatures = 0
    for filename in args.sigfiles:
        db = sourmash.load_file_as_index(filename)
        db = db.select(ksize=args.ksize, moltype='DNA')

        for ss in db.signatures():
            # note: flatten => count each hash only once,
            # independent of abundance
            flat_mh = ss.minhash.flatten()
            all_hashes.update(flat_mh.hashes)

            n_signatures += 1

    print(f"Loaded {len(all_hashes)} hashes from {n_signatures} sketches in {len(args.sigfiles)} files.")

    # find all hashes with abundance >= min_samples
    keep_hashes = set()
    min_samples = args.min_samples
    for hashval, v in all_hashes.items():
        # filter on minimum number of samples
        if v >= min_samples:
            keep_hashes.add(hashval)

    print(f'Of {len(all_hashes)} hashes, keeping {len(keep_hashes)} that are in {min_samples} or more samples.')

    save_sigs = sourmash_args.SaveSignaturesToLocation(args.output)
    save_sigs.open()

    # second pass: filter!
    for filename in args.sigfiles:
        db = sourmash.load_file_as_index(filename)
        db = db.select(ksize=args.ksize, moltype='DNA')

        for ss in db.signatures():
            mh = ss.minhash
            new_mh = mh.copy_and_clear()
            keep_these_hashes = keep_hashes.intersection(mh.hashes)

            # retain abundance, if present; else just add hashes.
            if mh.track_abundance:
                for hashval in keep_these_hashes:
                    abund = mh.hashes[hashval]
                    new_mh.add_hash_with_abundance(hashval, abund)
            else:
                new_mh.add_many(keep_these_hashes)

            new_ss = sourmash.SourmashSignature(new_mh, name=ss.name)

            save_sigs.add(new_ss)

    save_sigs.close()

    print(f"Saved {len(save_sigs)} signatures to '{args.output}'")
