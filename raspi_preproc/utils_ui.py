import sys
import os

class Logger(object):
    def __init__(self, output_file):
        self.terminal = sys.stdout
        self.log = open(output_file, "a")

    def write(self, message):
        self.terminal.write(message)
        if not self.log.closed:
            self.log.write(message)

    def close(self):
        self.log.close()

    def flush(self):
        self.close()
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass
