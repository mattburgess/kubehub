from flask import Flask
app = Flask(__name__)

@app.route("/api/kubernetes")
def kubernetes():
    pass
    #return "Hello World!"
