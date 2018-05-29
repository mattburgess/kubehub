from behave import given, when, then

@given(u'the API server is running')
def kubehub_setup(context):
    assert context.client
