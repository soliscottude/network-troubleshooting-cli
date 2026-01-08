import argparse
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

logger.addHandler(file_handler)


def main():
    parser = argparse.ArgumentParser(description="Minimal CLI + Logging example")
    parser.add_argument("--name", default="Scott", help="Name to greet")
    parser.add_argument("--count", type=int, default=3, help="How many times to greet")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    logger.info("Program started")

    i = 1
    while i <= args.count:
        logger.info("Greeting %d: Hello, %s!", i, args.name)
        i += 1

    logger.info("Program finished")


if __name__ == "__main__":
    main()
