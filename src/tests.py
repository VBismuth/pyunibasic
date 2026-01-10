# -*- coding: utf-8 -*-
""" Tests """

import time
import json
from typing import Any, Callable

from textdata import TextData, EOF
import ubml


def assert_test(got: Any, expected: Any, errmsg: str) -> str:
    """ Test if whe got what we expected """
    if got == expected:
        return 'SUCCESS'
    if errmsg:
        errmsg += '\n |' if errmsg[-1] != '\n' else ' |'
    return f'FAIL\n⤷|{errmsg}Expected: {str(expected)};\n |Got: {str(got)}'


def error_test(action: Callable, expected: Exception,
               args: tuple | None = None) -> str:
    """ Test if action throw an expected error """
    try:
        action(*args) if args else action()
    except expected:
        return 'SUCCESS'
    return f'FAIL\n⤷|Expected {expected} error, but passed'


def test_textdata():
    """ Testing text data """
    test_text = 'this is\na simple\ntext'
    td = TextData(test_text)
    for _ in range(6):
        td.next()

    assert td.get_char() == 's', f'Expected "s", got "{td.get_char()}"'
    assert td.get_text(end=td.get_pos()) == test_text[:td.get_pos()], \
        f'Expected {test_text[:td.get_pos()]}'\
        f', got: {td.get_text(end=td.get_pos())}'

    tmp = {'pos_lim': len(test_text), 'pos': 6, 'col': 7, 'ln': 1}
    assert td.get_pointer().as_dict() == tmp, f"Expected {tmp}, got: "\
        f"{td.get_pointer().as_dict()}"

    td.next()
    assert td.get_char() == '\n', \
        f'Expected newline, got? -> {td.get_char() == "\n"}'
    tmp = {'pos_lim': len(test_text), 'pos': 7, 'col': 8, 'ln': 1}
    assert td.get_pointer().as_dict() == tmp, f"Expected {tmp}, got: "\
        f"{td.get_pointer().as_dict()}"

    td.next()
    assert td.get_char() == 'a', f'Expected "a", got "{td.get_char()}"'
    tmp = {'pos_lim': len(test_text), 'pos': 8, 'col': 1, 'ln': 2}
    assert td.get_pointer().as_dict() == tmp, f"Expected {tmp}, got: "\
        f"{td.get_pointer().as_dict()}"

    td.previous()
    assert td.get_text(end=td.get_pos()) == test_text[:td.get_pos()], \
        f'Expected {test_text[:td.get_pos()]}'\
        f', got: {td.get_text(end=td.get_pos())}'
    tmp = {'pos_lim': len(test_text), 'pos': 7, 'col': 8, 'ln': 1}
    assert td.get_pointer().as_dict() == tmp, f"Expected {tmp}, got: "\
        f"{td.get_pointer().as_dict()}"

    for _ in test_text:
        td.next()
    assert td.get_char() == EOF, f'Couldnt get {EOF} at '\
        f'{td.get_pointer().as_dict()}'
    assert td.get_textsize() >= td.get_pos(), f'Pos {td.get_pos()} is more '\
        f'than textsize {td.get_textsize()}'

    td_copy = td.copy()
    td_copy.reset()
    assert td.get_text() == test_text, 'Text changed after reset'
    assert td == td_copy, 'TextData copy is not the same'

    td_copy.reset('This is aditional text')
    assert td != td_copy, 'TextData copy is still the '\
        'same after resetting with new text'
    assert (td + td).get_text() == test_text * 2, 'Addition is not working '\
        f'as intended {(td + td).get_text()} != {test_text * 2}'


def test_ubml():
    """ testing ubml """
    test_dict: dict = {'Name': 'John', 'Sirname': 'Williams', 'Age': 38,
                       'pets': [{'name': 'Adam', 'specie': 'cat'},
                                {'name': 'Tomas', 'specie': 'pig'}],
                       'Money': 34912.0398, 'Debt': -384.2, 'alive': True,
                       'Friends': None, 'Enemies': ['Craig']}

    assert ubml.loads(ubml.dumps(test_dict)) == test_dict, 'Something went' +\
        'wrong after serializing and deserealizing test_dict\n' +\
        f'Expected: {str(test_dict)}, ' +\
        f'Got: {str(ubml.loads(ubml.dumps(test_dict)))}'

    json_dict: str = json.dumps(test_dict, ensure_ascii=False)
    jsonlike_ubml_dict: str = ubml.dumps(test_dict, as_json=True)
    assert json_dict == jsonlike_ubml_dict, \
        'Json dump and ubml json-like dump are not the same\n' +\
        f'Expected: {json_dict}, Got: {jsonlike_ubml_dict}'

    ubml_expect1: str = 'Name=John,Sirname=Williams,Age=38,' +\
        'pets=[{name=Adam,specie=cat},{name=Tomas,specie=pig}],' +\
        'Money=34912.0398,Debt=-384.2,alive=true,friends=nil,' +\
        'Enemies=[Craig]'
    ubml_dumped1: str = ubml.dumps(test_dict)
    assert ubml_dumped1 == ubml_expect1, \
        'Actual dump and expected dump mismatch\n' +\
        f'Expected: {ubml_expect1}, Got: {ubml_dumped1}'

    try:
        ubml.loads('[test:]')
    except ubml.InvalidSymbolError:
        pass
    else:
        raise AssertionError('Expected error from "[test:]", but it passed')

    assert ubml.loads('[a, {b: c}]') == ['a', {'b': 'c'}], \
        'Wrong parsing [a, {b: c}]'


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
        print(f'Testing: {test.__name__} .', end='')
        try:
            print(' . ', end='')
            test_textdata()
            print('. ', end='')
        except (AssertionError, ubml.InvalidSymbolError,
                ubml.InvalidNumberError, ubml.NotSupported) as err:
            print('FAILURE\nGot:', err)
        else:
            print('SUCCESS')
            successes += 1
        print(f'Elapsed {time.perf_counter() - start_time} seconds\n')
    print(f'Finished tests in {time.perf_counter() - outer_start_time}',
          'seconds total')
    print(f'Result: {successes}/{counter}')


if __name__ == "__main__":
    main()
