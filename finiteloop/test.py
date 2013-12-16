

import unittest
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..')
path = os.path.realpath(path)
sys.path.append(path)

def suite():
    return unittest.TestLoader().discover(os.path.dirname(__file__))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
