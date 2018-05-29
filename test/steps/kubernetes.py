from behave import given, when, then

json = {}

@when(u'the user accesses the /api/kubernetes endpoint')
def step_impl(context):
    context.page = context.client.get('/api/kubernetes')

@then(u'500 repositories are returned')
def step_impl(context):
    assert context.page
