# python-aws-test-dump

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
