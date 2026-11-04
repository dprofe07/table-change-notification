import pytest

from . import validator


@pytest.mark.parametrize(
    'case,expected',
    [
        (1, True),
        (None, False),
        ('adasda', False),
    ]
)
def test_int(case, expected):
    pred_int = validator._expect_type(int)(validator._true)
    assert pred_int(case) == expected

@pytest.mark.parametrize(
    'case,expected',
    [
        ('22', True),
        ('222', True),
        ('aa', True),
        ('qq', True),
        ('qqa', False),
        ('dadas', False),
        ('2222', False),
        ('2', False),
        ('2a2', False),
    ]
)
def test_re_match(case, expected):
    pred_regex = validator._expect_regex(r'\d{2,3}|aa|qq')(validator._true)
    assert pred_regex(case) == expected

@pytest.mark.parametrize(
    'case,expected',
    [
        (1, False),
        (112312, False),
        (-1, True),
        (-100, True),
    ]
)
def test_custom_func(case, expected):
    pred_negative_int = validator.predicate(lambda t: t < 0)
    assert pred_negative_int(case) == expected

@pytest.mark.parametrize(
    'case,expected',
    [
        (1, False),
        ("2", False),
        ("@", False),
        ("-22", False),
        (None, False),
        (112312, False),
        (-1, True),
        (-100, True),
    ]
)
def test_composition(case, expected):
    pred_negative_and_int = validator.predicate(int, lambda t: t < 0)
    assert pred_negative_and_int(case) == expected
