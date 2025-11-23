from lexer import run

BASE = 'unibasic> '


if __name__ == '__main__':
    i: str = ''
    while i != 'quit':
        i = input(BASE)
        res, err = run(i)
        if err:
            print(err.as_str())
        else:
            print(res)
