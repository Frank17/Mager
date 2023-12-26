# Mager
A package aiming to automate the email-sending process and counter Python-related introspection issues.


## Installation

Mager can be installed using `pip` (no third-party dependencies needed): 
- `$ python3 -m pip install mager`


## Examples

**Send an email to specified recipients**
```py
from mager.gmail_manager import Sender, Info

sender = Sender(<your_email>, <your_app_pwd>)

rinfo = Info(
    recipients=[<email_1>, <email_2>, ..., <email_n>],
    name='Tester',
    subject='This is a test email',
    body='This is the email body.',
)

sender.send(rinfo)
```

**Send an email every 3 seconds, for a total of 5 emails**
```py
sender.send(rinfo, every='3s', mail_n=5)
```

**Use a custom template**
```py
from textwrap import dedent

body = dedent('''\
                Hi! Here's an image of a cute cat: $img1, and a smaller one: $img2,
                Click [here](https://imgur.com/gallery/VWjRf) to learn more about them.\
              ''')
img_url = 'https://i.imgur.com/AD3MbBi.jpeg'

rinfo = Info(
    recipients=[<email_1>, <email_2>, ..., <email_n>],
    name='Tester',
    subject='This is a test email',
    body=body,
    images=[img_url, (img_url, 'h150')]
)

sender.send(rinfo)
```

---

**Get the copy type** (works well for one-dimensional containers)
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

**Get the copy type recursively** (works well for nested containers)
```py
def get_copy_recursive(iter1, iter2):
    code = CopyChecker(iter1, iter2).check_copy(recursive=True)
    print(codes[code])


lst_with_mutable = [1, 2, (3, (4, [5]))]
get_copy_recursive(lst_with_mutable, copy(lst_with_mutable))        # shallow
get_copy_recursive(lst_with_mutable, deepcopy(lst_with_mutable))    # deep
```
---

## Next step
- Fix a minor bug in `CopyChecker` subpackage
- Add a new subpackage that supports HTML tables
