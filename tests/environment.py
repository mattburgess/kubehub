from kubehub import app

def before_feature(context, feature):
    context.client = app.test_client()
