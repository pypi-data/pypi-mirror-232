class Logger:
    """
    A simple logger class for printing log messages based on the specified log level.

    Attributes:
    logLevel (str): The log level to determine which messages to print ('verbose' or 'off').

    Methods:
    __init__(self, logLevel='verbose'): Initializes the Logger object with the specified log level.
    log(self, message): Logs the given message based on the log level.
    """

    def __init__(self, logLevel='verbose'):
        """
        Initialize the Logger object.

        Parameters:
        logLevel (str): The log level to determine which messages to print ('verbose' or 'off').
                        Default is 'verbose'.
        """
        self.logLevel = logLevel

    def log(self, message):
        """
        Log the given message based on the log level.

        Parameters:
        message (str): The message to be logged.
        """
        if self.logLevel == 'verbose':
            print(message)
