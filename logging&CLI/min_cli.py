import argparse


def main():
    parser = argparse.ArgumentParser(description="Minimal CLI example")
    parser.add_argument("--name", default="Scott", help="Name to greet")
    parser.add_argument("--count", type=int, default=3, help="How many times to greet")
    args = parser.parse_args()

    i = 1
    while i <= args.count:
        print("%d: Hellow, %s" % (i, args.name))
        i = i + 1


if __name__ == "__main__":
    main()
