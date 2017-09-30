# python-aws-test-dump

## !!! WARNING I am not responsible for what happens to your data so enter at your own risk !!!

Generally you will want to do a dump of some production data for fixtures to use in tests and make sure you aren't hitting production when using any of the restore classes or commands.

Take a look at the tests in the project to get an idea how to use for testing.  I'm using moto to mock aws with pytest which is fantastic!

This isn't meant to be a backup tool and won't handle large amounts of data.

## Usage

### dynamo schema

#### schema dump

To do a schema dump, run:

`aws_test_dump schema_dump --dump_file ~/big_dump.json`

or `aws_test_dump schema_dump` will dump to `tests/dynamo_schema_dump.json` by default

#### schema restore

To do a schema restore:

```python
import aws_test_dump

a = aws_test_dump.DynamoSchemaRestore('some/file/path')
a.run()
```

or to restore from the default location:

```python
import aws_test_dump

# name it something better than "a"
a = aws_test_dump.DynamoSchemaRestore()
a.run()
```
#### data dump

to dump data from a given table:

`aws_test_dump data_dump --table_name some_table_name`

The default dump directory will be

```python
os.getcwd(), 'tests/fixtures/dynamo_data_dumps')
```
but this can be overridden by passing the argument `--dump_dir`

`aws_test_dump data_dump --dump_dir some/directory --table_name some_table_name`

#### data restore

To restore files, run the following:

```python
    a = aws_test_dump.DynamoDataRestore()
    a.run()

    # default dump dir can be overridden here as well
    a = aws_test_dump.DynamoDataRestore(data_dump_dir='some/directory')
    a.run()
```


## data dump definition
You can make entries in the data dump definition which will be located in `tests/data_dump_definition.py` by default but can be overridden by setting the following:

`export DATA_DUMP_DEFINITION_MODULE=some.path.to.a.module`

An example can be seen in the tests which is using the default location.  Here it is again:

```python
from boto3.dynamodb.conditions import Key


DATA_DUMP_DEFINITION = [
    {
        'TableName': 'some_table_name',
        'KeyConditionExpression': Key('user_name').eq('chorizo'),
        'replace_first': {'user_name': {'S': 'chorizo'}},
    },
    {
        'TableName': 'some_other_table',
        'KeyConditionExpression': Key('another_id').eq('fake'),
        'replace_these': {
            'user_email': {'S': 'dan@dan.com'},
        },
        'replace_first': {
            'another_id': {'S': 'fake'},
            'customer_id': {'S': 'fake_id'},
        }
    }
]
```

Entries in replace_first will only be replaced on the first entry and replace_these will replaced on all items.
KeyConditionExpression will have your boto3 KeyConditionExpression.  See boto docs for more information on this.
The dump will do a scan of the table if there is no KeyConditionExpression however, I'm not doing any pagination.  This isn't meant to be a backup tool so only handles small amounts of data at the moment.

## Development

### Requirements
I started pinning the PyPI requirements using pip-tools.  More details here:

http://nvie.com/posts/pin-your-packages/
https://github.com/jazzband/pip-tools

Add a requirement to requirements.in and update requirements using pip-compile
This way we can pin the versions of dependencies and test them to ensure we aren't upgrading unintentionally if a dependency has broken backwards compatibility.


To update requirements, run:

```
pip-compile requirements.in
```

### Running Tests

I'm using pytest so to run tests, just:

`py.test`

for html coverage:

`coverage html`
