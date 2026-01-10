# -*- coding: utf-8 -*-
""" Tests """

import time
import json
from typing import Any, Callable

from textdata import TextData, EOF
import ubml


DEFAULT_LINE_SIZE: str = 80


def assert_test(got: Any, expected: Any, errmsg: str = '') -> str:
    """ Test if whe got what we expected """
    if got == expected:
        return 'SUCCESS'
    if errmsg:
        errmsg += '\n   |' if errmsg[-1] != '\n' else '  |'
    return f'FAIL\n  ⤷|{errmsg}Expected: {str(expected)};\n   |Got: {str(got)}'


def error_test(action: Callable, expected: Exception,
               args: tuple | None = None) -> str:
    """ Test if action throw an expected error """
    try:
        action(*args) if args else action()
    except expected:
        return 'SUCCESS'
    return f'FAIL\n⤷|Expected {expected} error, but passed'


def subtests_run(meta: dict, res: (str, bool)):
    """ Update test meta and print subtests result """
    meta['subtests_number'] += 1
    meta['successes'] += int(res[1])
    if meta['overall']:
        meta['overall'] = res[1]
    print(res[0])


def subtest_result(desc: str, result: str,
                   sep: str = '. ') -> (str, bool):
    ''' Subtest result '''
    default_len: int = DEFAULT_LINE_SIZE
    ending: str = ''

    if 'FAIL' in result and '\n' in result:
        result, ending = result.split('\n', maxsplit=1)

    # better to use len(n) - 1
    sep_mult: int = (default_len - len(desc) - len(result) - 2) // len(sep) - 1

    res: str = f'  * {desc} {sep * sep_mult}'
    len_diff = default_len - len(result + res) + 1
    res += ' ' * len_diff if len_diff > 0 else ''
    res += result + ('\n' if ending else '') + ending
    return res, 'FAIL' not in res


def test_textdata() -> dict:
    """ Testing text data """
    test_meta: dict = {'subtests_number': 0,
                       'successes': 0,
                       'overall': True}

    subtests_run(test_meta, subtest_result(
        'Empty TextData',
        assert_test(TextData('').get_text(), '')
    ))

    test_text = 'this is\na simple\ntext'
    td = TextData(test_text)

    for _ in range(6):
        td.next()

    subtests_run(test_meta, subtest_result(
        'Get char after 6 next() calls',
        assert_test(td.get_char(), 's')
    ))

    subtests_run(test_meta, subtest_result(
        'Get text up to current position',
        assert_test(
            td.get_text(end=td.get_pos()),
            test_text[:td.get_pos()],
            'Text mismatch'
        )
    ))

    tmp = {'pos_lim': len(test_text), 'pos': 6, 'col': 7, 'ln': 1}
    subtests_run(test_meta, subtest_result(
        'Pointer state checkup',
        assert_test(td.get_pointer().as_dict(), tmp, 'Pointer mismatch')
    ))

    td.next()
    subtests_run(test_meta, subtest_result(
        'Get newline character at current position',
        assert_test(td.get_char(), '\n', 'Expected newline')
    ))

    tmp = {'pos_lim': len(test_text), 'pos': 7, 'col': 8, 'ln': 1}
    subtests_run(test_meta, subtest_result(
        'Pointer state at newline character',
        assert_test(td.get_pointer().as_dict(), tmp, 'Pointer mismatch')
    ))

    td.next()
    subtests_run(test_meta, subtest_result(
        'Get character after newline',
        assert_test(td.get_char(), 'a', 'Expected "a"')
    ))

    tmp = {'pos_lim': len(test_text), 'pos': 8, 'col': 1, 'ln': 2}
    subtests_run(test_meta, subtest_result(
        'Pointer state after moving to the next line',
        assert_test(td.get_pointer().as_dict(), tmp, 'Pointer mismatch')
    ))

    td.previous()
    subtests_run(test_meta, subtest_result(
        'Get text after previous() call',
        assert_test(
            td.get_text(end=td.get_pos()),
            test_text[:td.get_pos()],
            'Text mismatch after previous()'
        )
    ))

    tmp = {'pos_lim': len(test_text), 'pos': 7, 'col': 8, 'ln': 1}
    subtests_run(test_meta, subtest_result(
        'Pointer state after previous()',
        assert_test(td.get_pointer().as_dict(), tmp, 'Pointer mismatch')
    ))

    for _ in test_text:
        td.next()

    subtests_run(test_meta, subtest_result(
        'EOF check at end of text',
        assert_test(td.get_char(), EOF, 'Could not get EOF')
    ))

    subtests_run(test_meta, subtest_result(
        'Position shouldn\'t be more than the text size',
        assert_test(
            td.get_textsize() >= td.get_pos(),
            True,
            f'Pos {td.get_pos()} is more than textsize {td.get_textsize()}'
        )
    ))

    td_copy = td.copy()
    td_copy.reset()
    subtests_run(test_meta, subtest_result(
        'Original text is the same after copy reset',
        assert_test(td.get_text(), test_text, 'Text changed after copy reset')
    ))

    subtests_run(test_meta, subtest_result(
        'TextData copy equality',
        assert_test(td, td_copy, 'TextData copy is not the same')
    ))

    td_copy.reset('This is additional text')
    subtests_run(test_meta, subtest_result(
        'TextData after reset with new text',
        assert_test(td != td_copy, True, 'TextData copy is still the same')
    ))

    subtests_run(test_meta, subtest_result(
        'Addition of TextData objects',
        assert_test(
            (td + td).get_text(),
            test_text * 2,
            'Addition is not working as intended'
        )
    ))
    return test_meta


def test_ubml() -> dict:
    """ testing ubml """
    test_meta: dict = {'subtests_number': 0,
                       'successes': 0,
                       'overall': True}

    subtests_run(test_meta, subtest_result(
        'Parsing empty string',
        assert_test(
            ubml.loads(''),
            {},
            'Wrong parsing of empty string'
        )
    ))

    subtests_run(test_meta, subtest_result(
        'Parsing nested structures [a, {b: c}]',
        assert_test(
            ubml.loads('[a, {b: c}]'),
            ['a', {'b': 'c'}],
            'Wrong parsing [a, {b: c}]'
        )
    ))

    test_dict: dict = {
        'Name': 'John',
        'Sirname': 'Williams',
        'Age': 38,
        'pets': [
            {'name': 'Adam', 'specie': 'cat'},
            {'name': 'Tomas', 'specie': 'pig'}
        ],
        'Money': 34912.0398,
        'Debt': -384.2,
        'alive': True,
        'Friends': None,
        'Enemies': ['Craig']
    }

    ubml_expect1: str = (
        'Name=John,Sirname=Williams,Age=38,'
        'pets=[{name=Adam,specie=cat},{name=Tomas,specie=pig}],'
        'Money=34912.0398,Debt=-384.2,alive=true,Friends=nil,'
        'Enemies=[Craig]'
    )
    ubml_dumped1: str = ubml.dumps(test_dict)
    subtests_run(test_meta, subtest_result(
        'UBML complex structure dump check',
        assert_test(
            ubml_dumped1,
            ubml_expect1,
            'Actual dump and expected dump mismatch'
        )
    ))

    subtests_run(test_meta, subtest_result(
        'Serialization and deserialization round-trip',
        assert_test(
            ubml.loads(ubml.dumps(test_dict)),
            test_dict,
            'Something went wrong after serializing '
            'and deserializing test_dict'
        )
    ))

    json_dict: str = json.dumps(test_dict, ensure_ascii=False)
    jsonlike_ubml_dict: str = ubml.dumps(test_dict, as_json=True)
    subtests_run(test_meta, subtest_result(
        'JSON and UBML JSON-like dump should be the same',
        assert_test(
            jsonlike_ubml_dict,
            json_dict,
            'Json dump and ubml json-like dump are not the same'
        )
    ))

    subtests_run(test_meta, subtest_result(
        'Invalid symbol error handling',
        error_test(
            lambda: ubml.loads('[test:]'),
            ubml.InvalidSymbolError
        )
    ))

    with open('tests.py', 'r', encoding='utf-8') as f:
        subtests_run(test_meta, subtest_result(
            'Loading invalid file (tests.py)',
            error_test(
                lambda: ubml.load(f),
                ubml.InvalidSymbolError
            )
        ))
    return test_meta


def main():
    """ Main function """
    print("Starting tests\n")
    outer_start_time: float = time.perf_counter()
    tests: tuple = (test_textdata, test_ubml)
    counter: int = 0
    successes: int = 0
    for test in tests:
        counter += 1
        start_time: float = time.perf_counter()
        meta: dict = {}
        print(f'Testing: {test.__name__}', '---{')  # }
        try:
            meta = test() or {'subtests_number': 0,
                              'successes': 0,
                              'overall': False}
        except Exception as err:
            print('}---> ERROR')
            raise err
        print('}--->', 'SUCCESS' if meta['overall'] else 'FAIL',
              f'[{meta['successes']}/{meta['subtests_number']}]')
        successes += 1 if meta['overall'] else 0
        print(f'Elapsed {time.perf_counter() - start_time} seconds\n')
    print('Overall:', 'SUCCESS' if successes == counter
          else 'FAIL', f'[{successes}/{counter}]')
    print(f'Finished tests in {time.perf_counter() - outer_start_time}',
          'seconds total')


if __name__ == "__main__":
    main()
