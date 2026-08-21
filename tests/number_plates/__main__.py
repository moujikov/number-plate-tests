import pytest
import sys
import os

test_dir = os.path.dirname(os.path.abspath(__file__))
sys.exit(pytest.main([test_dir, "-vv"]))
