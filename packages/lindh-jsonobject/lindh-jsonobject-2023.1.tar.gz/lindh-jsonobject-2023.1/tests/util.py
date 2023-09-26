import sys
import pytest


uses_typehints = pytest.mark.skipif(sys.version_info < (3, 7), reason="requires python3.7 or higher")
