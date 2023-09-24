"""tiktoken on the command line."""

import json
import sys

from argparse import ArgumentParser

import tiktoken

def main():
    parser = ArgumentParser(description="Encode or decode a file using tiktoken.")
    parser.add_argument("filename", nargs='?', type=str, help="The file to encode or decode.")
    parser.add_argument("-l", "--lines", action='store_true', default=False, help="Tokenize each line separately")
    
    outputs = parser.add_mutually_exclusive_group()
    outputs.add_argument("-d", "--decode", action='store_true', default=False, help="Whether to decode the input instead of encoding")
    outputs.add_argument("-c", "--count", action='store_true', default=False, help="Return the token count instead of the tokens")
    
    tkargs = parser.add_mutually_exclusive_group(required=True)
    tkargs.add_argument("-e", "--encoding", type=str, help="The encoding to use. Passed to tiktoken.get_encoder")
    tkargs.add_argument("-m", "--model", type=str, help="The model to use. Passed to tiktoken.encoder_for_model")
    
    args = parser.parse_args()

    tokenizer = None
    if args.encoding:
        tokenizer = tiktoken.get_encoding(args.encoding)
    elif args.model:
        tokenizer = tiktoken.encoding_for_model(args.model)

    if args.filename:
        with open(args.filename, 'r') as file:
            content = file.read()
    else:
        content = sys.stdin.read()

    
    if args.lines:
        content = content.split("\n")
    else:
        content = [content]

    for c in content:
        if args.decode:
            try:
                tokens: list[int] = json.loads(c)
                for i in tokens:
                    if not isinstance(i, int):
                        print("Error: Input should be a list of integers")
                        sys.exit(1)
            except:
                print("Invalid input")
                sys.exit(2)
            output = tokenizer.decode(tokens)
        else:
            output = tokenizer.encode(c)
        if args.count:
            print(len(output))
        else:
            print(output)

if __name__ == "__main__":
    main()



