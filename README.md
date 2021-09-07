# Important
I've be focusing on the base of this project [here](https://github.com/OpenQueue/Base), don't expect any of this to work until thats completed.

## Code layout

### Linting

Linted using PEP8 with a 80 character line limited, exceptions can be made by using `noqa: `, please be specific with the exceptions.

### Folder structure

- API
  - Response functions should be created under the correct version folder.
  - Decorators functions should be created under the correct version folder.
  - Models are to be created within a models folder in the root directory.

## Install

- cd into the project dir
- `pip3 install -e . --upgrade`
