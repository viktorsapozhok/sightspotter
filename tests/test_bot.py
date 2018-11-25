# A.Piskun
# 24/11/2018
#
# running tests from command line:
#       sightspotter> python -m pytest tests/
#
import os


def test_tokens():
    for var in ['SSB_TOKEN', 'SSB_TEST_TOKEN']:
        token = os.environ[var]
        prefix = token.split(':')[0]
        assert prefix.isdigit()
        assert len(prefix) == 9




