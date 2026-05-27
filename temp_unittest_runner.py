import os
import sys
import unittest

os.chdir(r'c:\Users\USER\hardwaremanagementsys')
loader = unittest.TestLoader()
suite = loader.discover('.', pattern='test*.py')
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
