import logger
log = logger.setup_applevel_logger(file_name = 'app_debug.log')
import mymodule
log.debug('Calling module function.')

mymodule.multiply(5, 2)
log.debug('Finished.')