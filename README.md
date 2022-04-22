# Mager
A module aims to address rare use cases you may encounter when dealing with built-in data types and structures

## Examples

**Get the copy type non-recursively** (suitable for one-dimensional container)
```py
from mager.copy_checker import CopyChecker, codes
from copy import copy, deepcopy

def get_copy(iter1, iter2):
    code = CopyChecker(iter1, iter2).check_copy()
    print(codes[code])


lst_with_mutable = [1, 2, [3]]
get_copy(lst_with_mutable, lst_with_mutable)                        # same ref
get_copy(lst_with_mutable, copy(lst_with_mutable))                  # shallow
get_copy(lst_with_mutable, deepcopy(lst_with_mutable))              # deep

lst_with_immutable = [1, 2, 3]
get_copy(lst_with_immutable, lst_with_immutable)                    # same ref
get_copy(lst_with_immutable, copy(lst_with_immutable))              # unidentifiable
get_copy(lst_with_immutable, deepcopy(lst_with_immutable))          # unidentifiable
```

**Get the copy type recursively** (suitable for multi-dimensional container)
```py
def get_copy_recursive(iter1, iter2):
    code = CopyChecker(iter1, iter2).check_copy(recursive=True)
    print(codes[code])


lst_with_mutable = [1, 2, (3, (4, [5]))]
get_copy_recursive(lst_with_mutable, copy(lst_with_mutable))        # shallow
get_copy_recursive(lst_with_mutable, deepcopy(lst_with_mutable))    # deep
```
