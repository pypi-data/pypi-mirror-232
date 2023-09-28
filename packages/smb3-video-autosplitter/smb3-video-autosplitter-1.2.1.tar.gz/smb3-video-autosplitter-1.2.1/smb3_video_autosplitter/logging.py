import logging

FILE_FORMAT = "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"


def initialize_logging(
    file_log_level="INFO",
    console_log_level="INFO",
    filename="smb3_video_autosplitter.log",
):
    # set up logging to file
    logging.basicConfig(
        filename=filename, level=file_log_level, format=FILE_FORMAT, datefmt="%H:%M:%S"
    )

    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(console_log_level)
    # set a format which is simpler for console use
    formatter = logging.Formatter("%(module)-12s: %(levelname)-8s %(message)s")
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger("").addHandler(console)
