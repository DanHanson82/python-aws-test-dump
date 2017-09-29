# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os

import boto3
import six


DYNAMO_DEFAULTS = {
    'region_name': os.environ.get('AWS_DEFAULT_REGION'),
    'endpoint_url': os.environ.get('DYNAMO_ENDPOINT'),
}

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
    if isinstance(obj, dict):
        return {
            k: keep_keys(key_names, v)
            for k, v in six.iteritems(obj) if k in key_names
        }
    elif isinstance(obj, list):
        return [keep_keys(key_names, i) for i in obj]
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
                os.getcwd(), 'tests/dynamo_data_dumps')
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

    def __init__(self, data_dump_definition, data_dump_dir=None, dump_file=None, dynamo_kwargs=None):
        super(DynamoTableDump, self).__init__(data_dump_dir, dump_file, dynamo_kwargs)
        self.table_name = data_dump_definition['TableName']
        self.data_dump_definition = data_dump_definition
        self._query_results = nil

    def get_default_dump_file(self):
        return os.path.join(self.data_dump_dir, self.table_name)

    def run(self):
        self.dump_data()

    def dump_data(self):
        data = {'table_name': self.table_name, 'data': self.query_results}
        if not os.path.exists(self._data_dump_dir):
            os.makedirs(self._data_dump_dir)
        with open(self.dump_file, 'wb') as fout:
            json.dump(data, fout, indent=2, sort_keys=True, encoding='utf-8')

    def _query(self):
        pass

    def _scan(self):
        pass

    @property
    def query_results(self):
        if self._query_results is None:
            if self.data_dump_definition['key_conditions']:
                self._query_results = self._query()
            else:
                self._query_results = self._scan()
        return self._query_results


class DynamoTableDataRestore(BaseDynamoProcessor):
    pass


class DynamoDataRestore(BaseDynamoProcessor):
    pass


class DynamoDataDump(BaseDynamoProcessor):
    pass



class S3Restore(BaseS3Processor):
    pass


class S3FileDump(BaseS3Processor):
    pass


class S3FileRestore(BaseS3Processor):
    pass
