import logging
import os
import sys


def prepare_logger():
    file_handler = logging.FileHandler(os.path.expanduser('~/hkust-fbs-automation.log'))
    file_handler.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setLevel(logging.INFO)
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s: %(message)s",
        level=logging.NOTSET,
        handlers=[file_handler, stream_handler],
    )

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.critical("Error uncaught: ", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception
