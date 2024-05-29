""" Classes for handling matrix files for specific apps. 

    Written by: Travis M. Moore
    Last edited: May 29, 2024
"""

###########
# Imports #
###########
# Standard library
import logging
import os
import sys

# Add custom path
try:
    sys.path.append(os.environ['TMPY'])
except KeyError:
    sys.path.append('C:\\Users\\MooTra\\Code\\Python')

# Custom
from tmpy.handlers import MatrixFile

##########
# Logger #
##########
logger = logging.getLogger(__name__)

##############
# HINTMatrix #
##############
class HINTMatrix(MatrixFile):
    """ Import a matrix file for use during session. """
    logger.debug("Initializing HINTMatrix")

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def import_matrix_file(self):
        """ Import matrix file. """
        try:
            # Import matrix file
            matrix_df = self.import_file(self.kwargs['filepath'])
            return matrix_df
        except TypeError as e:
            logger.error(e)


if __name__ == "__main__":
    pass
