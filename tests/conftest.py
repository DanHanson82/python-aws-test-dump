import os

import pytest


# we shouldn't be hitting aws here but just in case
os.environ['AWS_ACCESS_KEY_ID'] = 'fakeid'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'fakekey'
os.environ['AWS_REGION_NAME'] = 'us-west-2'

