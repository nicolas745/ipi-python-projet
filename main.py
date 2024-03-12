#!.venv/bin/python3
from flask import Flask, render_template
import sqlite3

class sql():
    def __init__(self,namefile) -> None:
        self.conn = sqlite3.connect(namefile)


class web():
    def __init__(self) -> None:
        app = Flask(__name__)
        @app.get("/")
        def index():
            varible = {
                "page":"index.html"
            }
            return self.render(**varible)
        if __name__ == '__main__':
            args = {
                'port':8080, #comme ameloration je peut utlise os.getenv('port') mais il faut charger le fichier lib python-dotenv la meme chose pour les autre
                'debug':True,
                'host':"0.0.0.0"
            }
            app.run(**args)
    def render(self,**args):
        return render_template("index.html",**args)
web()