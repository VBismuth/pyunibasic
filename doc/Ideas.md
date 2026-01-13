# Ideas
This file contains some ideas for the unibasic lang

## Important notes
- Make it so lexer could allow keyword starting with any letters
  or just create lexer for ubml, which is better imo (see [UBML](#UBML))
---

## What to add
- [ ] File worker (load files, zips, working with modules*)
- [ ] Modules (zip archive with files. See below)
- [x] UBML (unibasic markup lang, like jsonh or whatever)
- [ ] Subsets (unibasic in different lang, subset switches
- [ ] Errors for interpreter for the above
---

## Modules (file archives)
Modules should dump files into sutable form and pack them into zip archive.
(This zip archive will be named like *"Example.ubmod"* )
To 'mount' modules within ub program, use like MOUNTMOD('./path/to/module.ubmod')
Otherwise - UNMOUNTMOD('./path/to/module.ubmod')

**Steps**:
1. Make registry for the files
2. Find the file
3. Save its relative path, name and hash into registry (fileinfo entry)
4. Divide file into parts by defined size (i.e. 4096 kb - header size)
5. Put header to a var (with full obj hash), put part, name file with its hash
6. Save info for the file with part into the registry (filedata, enty of this file)
7. Put part into zip, arcname is dir with two first letters of the dumped file and the file itself
8. Repeat *5-4* steps for the every part
9. Repeat *2-8* for the every target files
10. Save registry into the zip as meta.ubml

Note: lookout for the hash collides
Note2: dump text files with pickle but in secure way
---

## Secure pickle
Got this idea from [SecurePickle](https://github.com/lpv2011/SecurePickle)

\[pyhton obj\] ---*serialization with pickle*---> \[pickled obj\]
                        pickle.dumps()          with hash


\[pyhton obj\] <---*deserialization with pickle*--- \[pickled obj\]
                        pickle.loads()            with hash

*Loads only if metadata (hash with file) is the same with hashed obj*

Note: Maybe just check every file by its hash
---

## UBML
Inspired by yaml and jsonh, also json compatible. It's supported by any UB interpreter. You can use it to store dicts/lists in unibasic, like
``` unibasic 
UBMLDUMPS(@obj, 'path/to/example.ubml'); @obj ! MAP = UBMLLOADS('path/to/example.ubml')```

Features:
- File is either list of objs (\[\]) or dict of objs ({})
- You can ommit braces for the file (not for data), it should detect automatically ({} by default)
- Strings without quotes, like {hello: world}. Also `hello\, this is \"whole\", and this is separated` will be parsed like this `['hello, this is "whole"', 'and this is separated']`
- Types of data:
    - String (simple_string, this also valid) - it may start with a number, but only in quotes
    - None (nil) - convert to None, or later into nil for ub interpreter
    - Bool (true or false) - convert to None, or later into nil for interpreter
    - Number (0.02, -23, etc) - convert to int or float
    - List
    - Dict
    - Comment (# This will be skipped)

---

## Subsets
The main idea is to let users code in their language, like
```unibasic
# $SUBSET "default"
PRINTLN "Hello, World"
```

will be
```unibasic
$SUBSET "ru_ru"
ВЫВОДНС "Привет, Мир"
```

## Anon functions
Like ``` FUNC () { PRINTLN 'ANON!'} ```

## Aliases
Call functions, builtins or const variables by alias name, so
```unibasic
FUNC sum(min, max, step):INT {
    LET answer:INT = 0
    LET i:INT = min
    UNTIL i >= max {
        i += step
        answer += 1
    }
    RETURN answer
}
# ...
ALIAS MULTIFUNC, FUNC () {LET name:STR = "Greg"; PRINTLN $"HELLO! {name}"}
ALIAS PRINTLNARGS($ARGS), PRINTLN $ARGS
ALIAS SUM_MIN_PLUS_ONE($ARGS), @sum($ARGS:0 + 1, $ARGS:1->2)
# ...
MULTIFUNC  # (HELLO! Greg)
PRINTLNARGS "This", " is ", $TO_STR(69)  # This is 69
SUM_MIN_PLUS_ONE  0, 4, 1  #  3
```

## API calls to interpreter
Get custom functions from interpreter realisation

