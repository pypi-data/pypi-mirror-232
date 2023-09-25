import pytest

from vina2vi.util import (
    rm_diacritics,
    normalize,
    cased_vina_normalizer,
)


@pytest.mark.xfail
def test_should_equal_diff_diacritics_rm_funcs():
    assert False


