import logging
import time
import random
logger = logging.getLogger()

def do_log(func):
    
    def wrapper(*args, **kwargs):
        logging.basicConfig(filename='myapp.log', level=logging.INFO)
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info(f"exec time: {end-start}")
        # print(f"exec time: {end-start}")
        return result
    return wrapper

@do_log
def func(id):
    time.sleep(2 * random.random())
    print(f"{id}")

func(4)