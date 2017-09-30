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
