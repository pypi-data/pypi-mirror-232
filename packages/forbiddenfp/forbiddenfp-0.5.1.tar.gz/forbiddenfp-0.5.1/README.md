# forbiddenfp

## Summary

Functional-Programming (FP) in a forbidden way.

Definitely Not Safe For Work.

```shell
pip install forbiddenfp
```

This library patches builtin `object` (and hence ALL classes),

with the ability to turn arbitrary function into postfix notation as function chaining.

The library already provides some patch for builtin/itertools functions.

Something like:

```python
# objects are already patched at import time
import forbiddenfp

"abc".then(lambda s: s * 2)  # "abcabc"
"abc".apply(print).len()  # print out "abc", then return 3
```

See more `./examples`.

## Known Issues

`None` doesn't work well with chained keyword arguments.

```python
import forbiddenfp

None.apply(print)  # works
None.apply(func=print)  # doesn't work
```
