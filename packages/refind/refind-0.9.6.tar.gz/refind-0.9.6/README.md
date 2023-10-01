# refind
A find clone in Python with both CLI and library interfaces

## Installation
This project is uploaded to PyPI at https://pypi.org/project/refind/

To install, ensure you are connected to the internet and execute: `python3 -m pip install refind`

## CLI Help
```
Partially implements find command entirely in Python.

    Usage: refind [path...] [expression...]

    default path is the current directory (.); default action is -print

    operators
        ! EXPR
        -not EXPR  Inverts the resulting value of the expression
        EXPR EXPR
        EXPR -a EXPR
        EXPR -and EXPR  Logically AND the left and right expressions' result
        EXPR -o EXPR
        EXPR -or EXPR   Logically OR the left and right expressions' result

    normal options
        -help  Shows help and exit
        -maxdepth LEVELS  Sets the maximum directory depth of find (default: inf)
        -mindepth LEVELS  Sets the minimum directory depth of find (default: 0)
        -regextype TYPE  Set the regex type to py, sed, egrep (default: sed)

    tests
        -name PATTERN  Tests against the name of item using fnmatch
        -regex PATTERN  Tests against the path to the item using re
        -type [dfl]  Tests against item type directory, file, or link
        -path PATTERN
        -wholename PATTERN  Tests against the path to the item using fnmatch
        -amin [+-]N  Last accessed N, greater than +N, or less than -N minutes ago
        -anewer FILE  Last accessed time is more recent than given file
        -atime [+-]N  Last accessed N, greater than +N, or less than -N days ago
        -cmin [+-]N  Change N, greater than +N, or less than -N minutes ago
        -cnewer FILE  Change time is more recent than given file
        -ctime [+-]N  Change N, greater than +N, or less than -N days ago
        -empty  File is 0 bytes or directory empty
        -executable  Matches items which are executable by current user
        -false  Always false
        -gid GID  Matches with group ID
        -group GNAME  Matches with group name or ID
        -mmin [+-]N  Modified N, greater than +N, or less than -N minutes ago
        -newer FILE  Modified time is more recent than given file
        -mtime [+-]N  Modified N, greater than +N, or less than -N days ago
        -newerXY REF  Matches REF X < item Y where X and Y can be:
                      a: Accessed time of item or REF
                      c: Change time of item or REF
                      m: Modified time of item or REF
                      t: REF is timestamp (only valid for X)
        -nogroup  Matches items which aren't assigned to a group
        -nouser  Matches items which aren't assigned to a user
        -perm [-/]PERM  Matches exactly bits in PERM, all in -PERM, any in /PERM
        -readable  Matches items which are readable by current user
        -true  Always true
        -uid UID  Matches with user ID
        -user UNAME  Matches with user name or ID
        -writable  Matches items which are writable by current user

    actions
        -print  Print the matching path
        -print0  Print the matching path without newline
        -printf  Print using find printf formatting
        -pyprint PYFORMAT  Print using python print() using named args:
                           find_root: the root given to refind
                           root: the directory name this item is in
                           rel_dir: the relative directory name from find_root
                           name: the name of the item
                           full_path: the full path of the item
                           mode_oct: st_mode as octal string
                           perm_oct: only the permissions part of mode_oct
                           perm: the permission in symbolic form
                           type: the type character
                           depth: the directory depth integer of this item
                           group: group name
                           user: user name
                           link: the file that this links to, if any
                           atime: access time as datetime
                           ctime: created time as datetime
                           mtime: modified time as datetime
                           any st args from os.stat()
        -pyprint0 PYFORMAT  Same as pyprint except end is set to empty string
        -exec COMMAND ;  Execute the COMMAND where {} in the command is the matching path
        -pyexec PYFORMAT ;  Execute the COMMAND as a pyformat (see pyprint)
        -delete  Deletes every matching path
```