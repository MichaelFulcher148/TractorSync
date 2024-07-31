import sys
from io import StringIO
import unittest
from unittest.mock import patch
from tractor_sync import main

class test_main_menu(unittest.TestCase):
    def open_main_menu(self):
        captured_text = StringIO()
        sys.stdout = captured_text
        main()

if __name__ == '__main__':
    unittest.main()
