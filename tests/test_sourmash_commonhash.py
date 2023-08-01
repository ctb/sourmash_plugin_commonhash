"""
Tests for sourmash_plugin_commonhash.
"""
import os
import pytest

import sourmash
import sourmash_tst_utils as utils
from sourmash_tst_utils import SourmashCommandFailed


def test_run_sourmash(runtmp):
    with pytest.raises(SourmashCommandFailed):
        runtmp.sourmash('', fail_ok=True)

    print(runtmp.last_result.out)
    print(runtmp.last_result.err)
    assert runtmp.last_result.status != 0                    # no args provided, ok ;)


def test_run_commonhash(runtmp):
    sig2 = utils.get_test_data('2.sig.gz')
    sig47 = utils.get_test_data('47.sig.gz')
    sig63 = utils.get_test_data('63.sig.gz')

    output = runtmp.output('commonhash.zip')

    runtmp.sourmash('scripts', 'commonhash', sig2, sig47, sig63,
                    '-o', output)

    print(runtmp.last_result.out)
    print(runtmp.last_result.err)
    assert runtmp.last_result.status == 0

    assert os.path.exists(output)
    output_sigs = sourmash.load_file_as_signatures(output)
    output_sigs = list(output_sigs)
    assert len(output_sigs) == 3

    assert 'Selecting k=31, DNA' in runtmp.last_result.out
    assert "Loaded 10587 hashes from 3 sketches in 3 files." in runtmp.last_result.out
    assert "Of 10587 hashes, keeping 2529 that are in 2 or more samples." in runtmp.last_result.out
