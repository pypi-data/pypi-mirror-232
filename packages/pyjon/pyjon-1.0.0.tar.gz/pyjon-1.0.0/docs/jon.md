# The JON (Just another Object Notation) language

The JON (Just another Object Notation) language is yet another language to describe data structures that supports many data types (strings, numbers, lists, dictionaries...). Here is an example of the structure of a JON file:

```jon
dict = {
    key = string
    key_0 = 0
    key_red = rgb { 1 0 0 }
    key_list = { string_1 "quoted_string_2" }
    key_sub_dict = {
        subkey = substring
    }
}
```


## Data types

The JON language includes a variety of data types (called `JONData`):
* `JONString`: string
* `JONNumber`: number (integer or decimal number)
* `JONQuotedString`: quoted string (a variant of `JONString` with quotes)
* `JONColor`: color (expressed in RGB, HSV or HSV360 format)
* `JONList`: lists of `JONData` (elements do not have to be of the same type)
* `JONDict`: lists of couple of `JONKey` and `JONData` (note that this representation does not make the "key" unique!)
* `JONKey`: key of a `JONDict` (same format as `JONString`)
* `JONDocument`: same as `JONDict`, but should not be nested in a `JONDict` or a `JONList`


## Formatting

JON files follow the same basic formatting rules that any other languages (expect 1 space between words, no trailing whitespace, all opened blocks should be closed...), even though `pyjon` should be able to load any file that do not include structural errors. To list the warnings and errors of a JON file, you can use the `validation()` function.
