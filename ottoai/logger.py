import logging

# Define a custom filter
class CustomFilter(logging.Filter):
    def __init__(self, start_string):
        super().__init__()
        self.start_string = start_string

    def filter(self, record):
        return record.getMessage().startswith(self.start_string)

# Custom logger class that automatically adds the filter
class FilteredLogger(logging.Logger):
    def __init__(self, name, start_string="[OTTO]"):
        super().__init__(name)
        self.addFilter(CustomFilter(start_string))

# Set the custom logger class
logging.setLoggerClass(FilteredLogger)

# Initialize the root logger
logging.basicConfig(level=logging.DEBUG)

# Add the filter to all existing loggers
for logger in logging.Logger.manager.loggerDict.values():
    if isinstance(logger, logging.Logger):  # Skip PlaceHolder objects
        logger.addFilter(CustomFilter("[OTTO]"))

# Test logs
logger = logging.getLogger("otto")