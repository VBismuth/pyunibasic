# -*- coding: utf-8 -*-
""" Tests """

from textdata import TextData, EOF


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


if __name__ == "__main__":

    print("Test start!")
    tests: tuple = (test_textdata,)
    for test in tests:
        print(f'Testing: {test.__name__}')
        test_textdata()
    print('Test end!')
