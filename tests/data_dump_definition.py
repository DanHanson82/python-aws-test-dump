

DATA_DUMP_DEFINITION = [
    {
        'TableName': 'some_table_name',
        'KeyConditionExpression': 'user_name = :user_name',
        'ExpressionAttributeValues': {":user_name": {'S': 'chorizo'}},
        'replace_first': {'user_name': {'S': 'chorizo'}},
    },
    {
        'TableName': 'some_other_table',
        'KeyConditionExpression': 'another_id = :another_id',
        'ExpressionAttributeValues': {":another_id": {'S': 'fake'}},
        'replace_these': {
            'user_email': {'S': 'dan@dan.com'},
        },
        'replace_first': {
            'another_id': {'S': 'fake'},
            'customer_id': {'S': 'fake_id'},
        }
    }
]
