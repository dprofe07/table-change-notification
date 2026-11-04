import re
from functools import reduce


def _build_predicate_builder(predicate):
    def decor(fn):
        def wrapper(arg):
            if predicate(arg):
                return fn(arg)
            return False
        return wrapper
    return decor


def _expect_type(expected: type):
    return _build_predicate_builder(lambda arg: isinstance(arg, expected))

def _expect_regex(regex: str):
    pattern = re.compile(regex)
    return _build_predicate_builder(lambda arg: re.fullmatch(pattern, arg))

def _true(*_):
    return True


def _prepare_predicate_fn(p):
    if isinstance(p, bool):
        return lambda a: p
    elif isinstance(p, str):
        return lambda fn: _expect_type(str)(_expect_regex(p)(fn))
    elif isinstance(p, type):
        return _expect_type(p)
    elif callable(p):
        return lambda fn: p
    else:
        return p


def predicate(*predicate_builders):
    return reduce(
        lambda a, i: _prepare_predicate_fn(i)(a),
        predicate_builders[::-1],
        _true
    )


class Validator:
    _VALID_PROFILE_DICT = {
        'statuses': predicate(dict, lambda x: all(isinstance(k, str) and isinstance(v, str) for k, v in x.items())),
        "worksheet": predicate(r"(\$D_number|\$first|\$\$.*|)"),
        "names-column": predicate(int),
        "first-task-column": predicate(int),
        "tasks-row": predicate(int),
        "task-number": predicate(r"(\$task-row|\$number)"),
        "table-key": predicate(str, lambda s: len(s) == 44),
    }
    _HELP_PROFILE_DICT = {
        'statuses': 'dict[str -> str]',
        'worksheet': '$D_number | $first | $$list-name',
        'names-column': 'int',
        'first-task-column': 'int',
        'tasks-row': 'int',
        'task-number': '$task-row | $number',
        'table-key': 'str with length == 44',
    }

    @classmethod
    def _validate_field(cls, name, value):
        return cls._VALID_PROFILE_DICT.get(name, _true)(value)

    @classmethod
    def validate(cls, data: dict) -> str | None:
        for _, prof in data.items():
            if not isinstance(prof, dict):
                return f'expected dict, found: {prof=}'

            for k, v in prof.items():
                if not cls._validate_field(k, v):
                    return f'invalid {k}: {v}, expected: {cls._HELP_PROFILE_DICT.get(k, '???')}'
        return None
