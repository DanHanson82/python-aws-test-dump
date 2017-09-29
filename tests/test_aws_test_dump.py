import json
import os

import pytest

from aws_test_dump import aws_test_dump


TEST_DATA_DIR = os.path.dirname(__file__)
DYNAMO_FIXTURES_DIR = os.path.join(TEST_DATA_DIR, 'fixtures/dynamo')
DYNAMO_SCHEMA_FILE = os.path.join(TEST_DATA_DIR, 'dynamo_schema_dump.json')
TEST_DUMP_FILE = os.path.join(TEST_DATA_DIR, 'tmp/dynamo_schema.json')


def test_dump(dynamo_fixture):
    a = aws_test_dump.DynamoSchemaRestore(DYNAMO_SCHEMA_FILE)
    a.run()
    a = aws_test_dump.DynamoSchemaRestore(DYNAMO_SCHEMA_FILE)
    a.run()
    a = aws_test_dump.DynamoSchemaDump(TEST_DUMP_FILE)
    a.run()
