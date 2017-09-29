import os

from moto import mock_dynamodb2, mock_s3
import pytest


# we shouldn't be hitting aws here but just in case
os.environ['AWS_ACCESS_KEY_ID'] = 'fakeid'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'fakekey'
os.environ['AWS_REGION_NAME'] = 'us-west-2'


@pytest.fixture(scope='session')
def dynamo_fixture(request):
    mock = mock_dynamodb2()
    mock.start()
    request.addfinalizer(mock.stop)
