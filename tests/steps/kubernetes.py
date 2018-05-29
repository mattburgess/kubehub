from behave import given, when, then

@when(u'the user accesses the /api/kubernetes endpoint')
@then(u'500 repositories are returned')
def kubernetes(context):
    context.page = context.client.get('/api/kubernetes')
    assert context.page
