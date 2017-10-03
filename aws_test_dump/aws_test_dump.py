# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from copy import deepcopy
import decimal
import importlib
import json
import os
import sys

import boto3
import six


data_dump_definition_module = os.environ.get(
    'DATA_DUMP_DEFINITION_MODULE') or 'tests.data_dump_definition'
try:
    test_data_dump_definition = importlib.import_module(data_dump_definition_module)
    DATA_DUMP_DEFINITION = test_data_dump_definition.DATA_DUMP_DEFINITION
except ImportError:
    DATA_DUMP_DEFINITION = []


DYNAMO_DEFAULTS = {
    'region_name': os.environ.get('AWS_DEFAULT_REGION'),
    'endpoint_url': os.environ.get('DYNAMO_ENDPOINT'),
}
DYNAMODB_RESOURCE = boto3.resource('dynamodb', **DYNAMO_DEFAULTS)

S3_DEFAULTS = {
    'region_name': os.environ.get('AWS_DEFAULT_REGION'),
    'endpoint_url': os.environ.get('FAKES3_ENDPOINT'),
}


DYNAMO_TABLE_FIELDS = (
    'AttributeDefinitions'
    'AttributeName'
    'AttributeType'
    'GlobalSecondaryIndexes'
    'IndexName'
    'KeySchema'
    'KeyType'
    'LocalSecondaryIndexes'
    'NonKeyAttributes'
    'Projection'
    'ProjectionType'
    'ProvisionedThroughput'
    'ReadCapacityUnits'
    'StreamEnabled'
    'StreamSpecification'
    'StreamViewType'
    'TableName'
    'WriteCapacityUnits'
)


def keep_keys(key_names, obj):
    if hasattr(obj, 'items') or hasattr(obj, 'iteritems'):
        return {
            k: keep_keys(key_names, v)
            for k, v in six.iteritems(obj) if k in key_names
        }
    elif hasattr(obj, '__iter__'):
        return [keep_keys(key_names, i) for i in obj]
    else:
        return obj


def cast_decimals(obj):
    if hasattr(obj, 'items') or hasattr(obj, 'iteritems'):
        return {k: cast_decimals(v) for k, v in six.iteritems(obj)}
    elif hasattr(obj, '__iter__'):
        if isinstance(obj, set):
            obj = list(obj)
        return [cast_decimals(i) for i in obj]
    elif isinstance(obj, decimal.Decimal):
        return str(obj)
    else:
        return obj


class BaseProcessor(object):

    def run(self):
        raise NotImplementedError


class BaseDynamoProcessor(BaseProcessor):

    def __init__(self, dump_file=None, dynamo_kwargs=None):
        dynamo_lookup = dynamo_kwargs or DYNAMO_DEFAULTS
        self.dynamo_client = boto3.client('dynamodb', **dynamo_lookup)
        self._dump_file = dump_file

    def get_default_dump_file(self):
        raise NotImplementedError

    @property
    def dump_file(self):
        if self._dump_file is None:
            self._dump_file = self.get_default_dump_file()
        return self._dump_file


class BaseS3Processor(BaseProcessor):
    pass


class BaseDynamoSchema(BaseDynamoProcessor):

    def get_default_dump_file(self):
        return os.path.join(os.getcwd(), 'tests/dynamo_schema_dump.json')


class BaseDynamoData(BaseDynamoProcessor):

    def __init__(self, data_dump_dir=None, dump_file=None, dynamo_kwargs=None):
        super(BaseDynamoData, self).__init__(dump_file, dynamo_kwargs)
        self._data_dump_dir = data_dump_dir

    @property
    def data_dump_dir(self):
        if self._data_dump_dir is None:
            self._data_dump_dir = os.path.join(
                os.getcwd(), 'tests/fixtures/dynamo_data_dumps')
        return self._data_dump_dir


class DynamoSchemaDump(BaseDynamoSchema):

    def __init__(self, dump_file=None, dynamo_kwargs=None):
        super(DynamoSchemaDump, self).__init__(dump_file, dynamo_kwargs)
        self._table_names = None
        self._schemata = None

    def run(self):
        self._dump_schemata()

    def _dump_schemata(self):
        dump_dir = os.path.dirname(self.dump_file)
        if not os.path.exists(dump_dir):
            os.makedirs(dump_dir)
        with open(self.dump_file, 'wb') as fout:
            json.dump(
                self.schemata, fout, indent=2, sort_keys=True,
                encoding='utf-8')

    @property
    def schemata(self):
        if self._schemata is None:
            self._schemata = [
                keep_keys(
                    DYNAMO_TABLE_FIELDS,
                    self.dynamo_client.describe_table(
                        TableName=table_name)['Table'])
                for table_name in self.table_names
            ]
        return self._schemata

    @property
    def table_names(self):
        if self._table_names is None:
            self._table_names = self.dynamo_client.list_tables()['TableNames']
        return self._table_names


class DynamoSchemaRestore(BaseDynamoSchema):

    def __init__(self, dump_file=None, dynamo_kwargs=None):
        super(DynamoSchemaRestore, self).__init__(dump_file, dynamo_kwargs)
        self._schemata = None

    def run(self):
        self.create_tables()

    def create_tables(self):
        for schema in self.schemata:
            try:
                self.dynamo_client.create_table(**schema)
            except self.dynamo_client.exceptions.ResourceInUseException:
                continue

    @property
    def schemata(self):
        if self._schemata is None:
            with open(self.dump_file, 'r') as fin:
                self._schemata = json.loads(fin.read())
        return self._schemata


class DynamoTableDump(BaseDynamoData):

    def __init__(self, data_dump_definition=None, table_name=None, data_dump_dir=None, dump_file=None, dynamo_kwargs=None):
        super(DynamoTableDump, self).__init__(data_dump_dir, dump_file, dynamo_kwargs)
        self.data_dump_definition = data_dump_definition or {}
        self.table_name = self.data_dump_definition.get('TableName') or table_name
        self._query_results = None

    def get_default_dump_file(self):
        return os.path.join(
            self.data_dump_dir, '{}.json'.format(self.table_name))

    def run(self):
        self.dump_data()

    def dump_data(self):
        data = {
            'table_name': self.table_name,
            'data': cast_decimals(self.query_results)
        }
        if not os.path.exists(self.data_dump_dir):
            os.makedirs(self._data_dump_dir)
        with open(self.dump_file, 'wb') as fout:
            json.dump(data, fout, indent=2, sort_keys=True, encoding='utf-8')

    def _query(self):
        return self.dynamo_client.query(
            TableName=self.table_name,
            KeyConditionExpression=self.data_dump_definition.get('KeyConditionExpression'),
            ExpressionAttributeValues=self.data_dump_definition.get('ExpressionAttributeValues', {}),
            #ExpressionAttributeNames=self.data_dump_definition.get('ExpressionAttributeNames', {}),
        )

    def _scan(self):
        return self.dynamo_client.scan(TableName=self.table_name)

    @property
    def query_results(self):
        if self._query_results is None:
            if self.data_dump_definition.get('KeyConditionExpression'):
                self._query_results = self._query()
            else:
                self._query_results = self._scan()
        return self._query_results


class DynamoDataDump(BaseDynamoProcessor):
    def __init__(self, table_name=None, data_dump_dir=None, dynamo_kwargs=None):
        super(DynamoDataDump, self).__init__(None, dynamo_kwargs)
        self._data_dump_definitions = None
        self.table_name = table_name
        self.data_dump_dir = data_dump_dir

    @property
    def data_dump_definitions(self):
        if self._data_dump_definitions is None:
            self._data_dump_definitions = deepcopy(DATA_DUMP_DEFINITION)
            if self.table_name:
                self._data_dump_definitions = [
                    i for i in self._data_dump_definitions
                    if i.get('TableName') == self.table_name
                ]
        return self._data_dump_definitions

    def run(self):
        if self.data_dump_definitions:
            for data_dump_definition in self.data_dump_definitions:
                dynamo_table_dump = DynamoTableDump(
                    data_dump_definition=data_dump_definition,
                    data_dump_dir=self.data_dump_dir
                )
                dynamo_table_dump.run()
        elif self.table_name:
            dynamo_table_dump = DynamoTableDump(
                table_name=self.table_name,
                data_dump_dir=self.data_dump_dir
            )
            dynamo_table_dump.run()


class DynamoTableDataRestore(BaseDynamoProcessor):
    def __init__(self, file_path, dynamo_kwargs=None):
        super(DynamoTableDataRestore, self).__init__(None, dynamo_kwargs=dynamo_kwargs)
        self.file_path = file_path
        self._table_name = None
        self._data = None
        self._data_dump_definition = None

    def run(self):
        for index, item in enumerate(self.data):
            replace_first = self.data_dump_definition.get('replace_first')
            replace_these = self.data_dump_definition.get('replace_these')
            if index == 0 and replace_first:
                item.update(replace_first)
            if replace_these:
                item.update(replace_these)

            self.dynamo_client.put_item(
                TableName=self.table_name, Item=item
            )

    def _parse_file(self):
        with open(self.file_path, 'r') as fin:
            file_contents = json.loads(fin.read())
        self._table_name = file_contents['table_name']
        self._data = file_contents['data']['Items']

    @property
    def table_name(self):
        if self._table_name is None:
            self._parse_file()
        return self._table_name

    @property
    def data(self):
        if self._data is None:
            self._parse_file()
        return self._data

    @property
    def data_dump_definition(self):
        if self._data_dump_definition is None:
            definition = [
                i for i in DATA_DUMP_DEFINITION
                if i.get('TableName') == self.table_name
            ]
            if definition:
                self._data_dump_definition = definition[0]
            else:
                self._data_dump_definition = {}
        return self._data_dump_definition


class DynamoDataRestore(BaseDynamoData):

    def __init__(self, data_dump_dir=None, dump_file=None, dynamo_kwargs=None):
        super(DynamoDataRestore, self).__init__(data_dump_dir, dump_file, dynamo_kwargs)
        self._data_dump_files = None
        self.dynamo_kwargs = dynamo_kwargs

    @property
    def data_dump_files(self):
        if self._data_dump_files is None:
            self._data_dump_files = [
                os.path.join(self.data_dump_dir, f)
                for f in os.listdir(self.data_dump_dir)
                if f.endswith('.json')
            ]
        return self._data_dump_files

    def run(self):
        for data_dump_file in self.data_dump_files:
            dynamo_table_data_restore = DynamoTableDataRestore(data_dump_file, self.dynamo_kwargs)
            dynamo_table_data_restore.run()


class S3Restore(BaseS3Processor):
    pass


class S3FileDump(BaseS3Processor):
    pass


class S3FileRestore(BaseS3Processor):
    pass
