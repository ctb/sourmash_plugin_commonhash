# sourmash_plugin_commonhash

This plugin helps in situations where you have sketched many samples
and you want to remove k-mers that are present in 1 (or only a few)
samples. This helps reduce noise in Jaccard comparisons between samples.

See
[sourmash#2383](https://github.com/sourmash-bio/sourmash/issues/2383)
for an extended discussion!

Thanks to Taylor Reiter and Jessica Lumian for all their work on this!

## Installation

```
pip install sourmash_plugin_commonhash
```

## Usage

```
sourmash scripts commonhash <multiple sketches> -o commonhashes.zip
```

commonhash will output one filtered sketch for _each_ input sketch.
You can then use the various `sourmash sig` commands to union these
sketches, extract individual ones, etc.

### Example

```
sourmash scripts commonhash 
```

should yield:

```
...

Selecting k=31, DNA
Loaded 10587 hashes from 3 sketches in 3 files.
Of 10587 hashes, keeping 2529 that are in 2 or more samples.
Saved 3 signatures to 'commonhash.zip'
```

## Support

We suggest filing issues in [the main sourmash issue tracker](https://github.com/dib-lab/sourmash/issues) as that receives more attention!

## Dev docs

`commonhash` is developed at https://github.com/ctb/sourmash_plugin_commonhash.

### Generating a release

Bump version number in `pyproject.toml` and push.

Make a new release on github.

Then pull, and:

```
python -m build
```

followed by `twine upload dist/...`.
