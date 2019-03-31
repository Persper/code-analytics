# Java Antlr Parser

This directory contains the generated parser and listener for this optimized Antlr [grammar](https://github.com/antlr/grammars-v4/tree/master/java) for Java 7 & 8. It is roughly 200x faster than the more complete Java 8 grammar on average.


## How it's generated?

First, install Antlr4, please see instructions [here](https://github.com/antlr/antlr4/blob/master/doc/getting-started.md).

Then generate the parser and listener with the following command:

```
antlr4 -Dlanguage=Python3 JavaLexer.g4 JavaParser.g4
```

## How to use it?

The easiest way to use this parser is to create a custom listener, please see this [example](https://github.com/antlr/antlr4/blob/master/doc/python-target.md#how-do-i-create-and-run-a-custom-listener).
