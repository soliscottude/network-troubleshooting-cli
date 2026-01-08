import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    try:
        1 / 0
    except ZeroDivisionError:
        logger.error("Something went wrong!", exc_info=True)


if __name__ == "__main__":
    main()
