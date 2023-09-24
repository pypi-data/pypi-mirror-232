# `tkn`

`tkn` is a command-line utility to quickly tokenize with `tiktoken`.

## Installation

`pip install tkn`

Example usage:

```
$ ls
document_1.txt
document_2.txt

$ tkn document_1.txt
[tokenized version of the data]

$ tkn document_1.txt -s '\n' | wc -l
2094 # document contains 2094 tokens

$ tkn -m gpt-4 document_1.txt | tkn -m gpt-4 -d
[the contents of document_1.txt]
