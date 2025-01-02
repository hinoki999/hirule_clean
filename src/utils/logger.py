import logging

def setup_logging():
    """
    Configures the logging for the application.
    """
    logging.basicConfig(
        level=logging.DEBUG,  # Set to DEBUG for detailed logs; adjust as needed
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


