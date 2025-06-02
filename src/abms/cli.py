import argparse, sys
from pathlib import Path
from .encoder import encode_file


def _cmd_encode(argv):
    p = argparse.ArgumentParser(prog="abms encode",
                                description="Batch-encode a *.clean.jsonl file")
    p.add_argument("input",  type=Path)
    p.add_argument("-o", "--output", type=Path,
                   help="target (.tags.jsonl). Default: <input>.tags.jsonl")
    encode_args = p.parse_args(argv)

    out = encode_args.output or encode_args.input.with_suffix(".tags.jsonl")
    encode_file(encode_args.input, out)


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        print("usage: abms encode <in.clean.jsonl> [-o out.tags.jsonl]")
        sys.exit(0)

    cmd, *rest = sys.argv[1:]
    if cmd == "encode":
        _cmd_encode(rest)
    else:
        sys.stderr.write(f"abms: unknown sub-command '{cmd}'\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
