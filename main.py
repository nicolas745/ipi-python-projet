#!.venv/bin/python3
from flask import Flask, render_template
app = Flask(__name__)


def render(**args):
    return render_template("index.html",**args)

@app.get("/")
def index():
    varible = {
        "page":"index.html"
    }
    return render(**varible)
if __name__ == '__main__':
    args = {
        'port':8080, #comme ameloration je peut utlise os.getenv('port') mais il faut charger le fichier lib python-dotenv la meme chose pour les autre
        'debug':True,
        'host':"0.0.0.0"
    }
    app.run(**args)