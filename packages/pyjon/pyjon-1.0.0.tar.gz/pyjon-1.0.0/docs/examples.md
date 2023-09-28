# Examples

This document constitutes a non-exhaustive list of the basic usages of the `pyjon` package.


## Load a JON file

```python
import jon

with open('example.jon', 'r', encoding='utf-8-sig') as file:
    object = jon.load(file.read())
```


## Display a JON data object

```python
from jon import JONDict

object = JONDict()
print(object.json())
```


## List validation errors of a JON text

```python
from jon import validate

text_with_errors = """
object = {
    key_without_value =
    key_no_space=value_no_space
    list_not_closed = { element_1 element_2
}
"""
validation_errors = validate(text)
```


## Get the semantic tokens of a JON string

```python
from jon import get_tokens

text = """
object = {
    key = value
    key_number = 1
    list = { element_1 element_2 }
}
"""
get_tokens(text)
```

