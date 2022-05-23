import logger
log = logger.get_logger(__name__)

def multiply(num1, num2): # just multiply two numbers
    log.debug("Executing multiply function.")
    return num1 * num2