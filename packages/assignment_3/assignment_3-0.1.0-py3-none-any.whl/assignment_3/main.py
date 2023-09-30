import logging

from foxlogger import FoxLogger

if __name__ == "__main__":
    logger = FoxLogger("example_logger")

    logger.info("This is an informational message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")