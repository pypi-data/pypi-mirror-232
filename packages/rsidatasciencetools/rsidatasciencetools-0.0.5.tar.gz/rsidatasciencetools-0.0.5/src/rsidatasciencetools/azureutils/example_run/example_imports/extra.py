'''test import file'''
import os

# NOTE: Relative imports rely on the __name__ or __package__ variable 
# (which is __main__ and None for a script, respectively), which is why 
# this extra.py module is inside the `example_imports` folder with 
# an `__init__.py` file to indicate a package. There are other approaches
# that can be used, including update the python path, but this is the
# simplest for use with Azure cloud model training.

def test_func(input):
    return 'your input was: ' + str(input)

