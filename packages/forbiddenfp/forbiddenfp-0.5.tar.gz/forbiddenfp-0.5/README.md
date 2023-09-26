# forbiddenfp

Functional-Programming (FP) in a forbidden way.

```shell
pip install forbiddenfp
```

This library patches builtin objects - so definitely Not Safe For Work.

But you achieve something like:

```python
# import already patches objects
import forbiddenfp

"abc".then(lambda s: s * 2)  # "abcabc"
"abc".apply(print).then(len) # print out "abc", then return 3
```

See more `./examples`.
