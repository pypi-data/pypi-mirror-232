# fkeycapture
This is a simple and easy to use package that allows you to capture individual keystrokes from the user.
#### Forms:
1. (Default) Recive key as a string
2. Recive key as bytes (get only)
3. Recive key as ints  (getnum only)
#### How to Use:
1. from fkeycapture import get, getnum, getchars
2. Use get like this: `get(keycount = any int, bytes = True or False)`
3. Use getnum like this: `getnum(keycount = any int, ints = True or False)`
4. Use getchars like this: `getchars(keycount = any int, chars = list of chars, bytes = True or False)`
#### Change log:
###### v.1.2.7:
Make some small type hinting changes, update `.pyi` file
###### v.1.2.6:
Add new option to use `os.read` instead of `sys.stdin.read`
###### v.1.2.5:
Add support for deleting chars in all methods, also completely removed the help command from the code for space reasons
###### v.1.2.4:
Mypy support
###### v.1.2.3:
Project links updated
###### v.1.2.2:
Internal improvements, Changelog improved
###### v.1.2.1:
Changelog issue fixed, removed the help command from 1.0.10
###### v.1.2.0
Type hinting, docstrings, and int support for getnum!
###### v.1.0.10
~~Now includes a help command! Use fkeycapture.help() to recive help.~~ See v.1.2.1
###### v.1.0.9
Fixed README issues in 1.0.8
###### v.1.0.8
Added getchars method
###### v.1.0.7
Added the getnum method
###### v.1.0.6
Finally made the package usable.
###### v.1.0.5
Repaired an issue in 1.0.4 which caused the module to cause a recusion error.
###### v.1.0.4
Repaired an issue in 1.0.3 which caused the module to be unusable.
###### v.1.0.3
Repaired an issue in 1.0.0, 1.0.1, and 1.0.2 which caused the module to be unusable.
###### v.1.0.2 (Missing)
Unknown
###### v.1.0.1
Corrected incorrect text in certain files
###### v.0.0.6 (v.1.0.0 on PyPI)
Removed unnecessary code
###### v.0.0.5
Replit support?