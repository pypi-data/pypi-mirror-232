import logging

def setup_logger(name='test', log_file='logs.txt'):
    logging.basicConfig(level = 'INFO', filename='1.log' )
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    


    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.debug(f'{formatter}')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
        # logger.addHandler(file_handler)

    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.INFO)
    # console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logging.shutdown()

    return logger

setup_logger()