import json
import os

import pytest

from aws_test_dump import aws_test_dump


TEST_DATA_DIR = os.path.dirname(__file__)
DYNAMO_FIXTURES_DIR = os.path.join(TEST_DATA_DIR, 'fixtures/dynamo')
DYNAMO_SCHEMA_FILE = os.path.join(TEST_DATA_DIR, 'dynamo_schema_dump.json')
TEST_DUMP_DIR = os.path.join(TEST_DATA_DIR, 'tmp')
TEST_DUMP_FILE = os.path.join(TEST_DUMP_DIR, 'dynamo_schema.json')
TEST_DUMP_DYNAMO = os.path.join(TEST_DUMP_DIR, 'dynamo')


def test_dump():
    # TODO: clean these up and make some more useful assertions
    a = aws_test_dump.DynamoSchemaRestore(DYNAMO_SCHEMA_FILE)
    a.run()
    a = aws_test_dump.DynamoSchemaRestore(DYNAMO_SCHEMA_FILE)
    a.run()
    a = aws_test_dump.DynamoSchemaDump(TEST_DUMP_FILE)
    a.run()
    a = aws_test_dump.DynamoDataRestore()
    a.run()
    a = aws_test_dump.DynamoDataDump(
        table_name='some_table_name', data_dump_dir=TEST_DUMP_DYNAMO
    )
    a.run()
    a = aws_test_dump.DynamoDataDump(
        table_name='some_other_table', data_dump_dir=TEST_DUMP_DYNAMO
    )
    a.run()
    a = aws_test_dump.DynamoDataDump(
        table_name='last_table', data_dump_dir=TEST_DUMP_DYNAMO
    )
    a.run()


def test_restore():
    # TODO: clean these up and make some more useful assertions
    a = aws_test_dump.DynamoSchemaRestore(TEST_DUMP_FILE)
    a.run()
    a = aws_test_dump.DynamoSchemaRestore(TEST_DUMP_FILE)
    a.run()
    a = aws_test_dump.DynamoDataRestore(TEST_DUMP_DYNAMO)
    a.run()
