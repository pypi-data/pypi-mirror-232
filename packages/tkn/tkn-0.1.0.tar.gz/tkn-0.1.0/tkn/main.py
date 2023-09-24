import tiktoken
from argparse import ArgumentParser
import sys

def main():
    parser = ArgumentParser(description="Encode or decode a file using tiktoken.")
    parser.add_argument("filename", nargs='?', type=str, help="The file to encode or decode.")
    parser.add_argument("-d", "--decode", action='store_true', default=False, help="Whether to decode the file.")
    parser.add_argument("-s", "--split", action='store_true', default=False, help="Tokenize each line separately")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-e", "--encoding", type=str, help="The encoding to use. Passed to tiktoken.Tokenizer")
    group.add_argument("-m", "--model", type=str, help="The model to use. Passed to tiktoken.Tokenizer.from_pretrained")
    
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

    
    if args.split:
        content = content.split("\n")
    else:
        content = [content]

    for c in content:
        if args.decode:
            output = tokenizer.decode(c)
        else:
            output = tokenizer.encode(c)
        print(f"[{','.join(map(str, output))}]")

if __name__ == "__main__":
    main()



