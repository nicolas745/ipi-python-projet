#!.venv/bin/python3
from flask import Flask, render_template
from hashlib import sha256
import sqlite3
from enum import Enum

class env(Enum):
    USER="pseudo"
    PASSWD="passwd"
    INDEX="index.html"
    ERROR404 ="404.html"
class sql():
    USER="pseudo"

    def __init__(self,namefile:str) -> None:
        self.conn = sqlite3.connect(namefile)
        cusor =self.conn.cursor()
        cusor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {} TEXT,
                {} TEXT
            );
        '''.format(env.PASSWD.value,env.USER.value))
        cusor.close()
        self.conn.commit()
    def ischeckuser(self):
        cursor=self.conn.cursor()
        cursor.execute("SELECT * FROM user WHERE user",())
        cursor.close()
class web():
    def __init__(self,app:Flask) -> None:
        pass
    def render(self,**args):
        return render_template("index.html",**args)
class principal(web):
    def __init__(self,app:Flask) -> None:
        self.sql = sql("database.db")
        @app.get("/")
        def index():
            varible = {
                "page":env.INDEX.value
            }
            return self.render(**varible)
        
        @app.post("/")
        def connect():
            varible = {
                "page":env.INDEX.value
            }
            return self.render(**varible)
        
        @app.get("/register")
        def fromregister():
            varible = {
                "page":env.INDEX.value
            }
            return self.render(**varible)
        @app.errorhandler(404)
        def page_not_found(e):
            varible = {
                "page":env.ERROR404.value
            }
            return self.render(**varible), 404
app = Flask(__name__)
principal(app)
if __name__ == '__main__':
    args = {
        'port':8080,  #comme ameloration je peut utlise os.getenv('port') mais il faut charger le fichier lib python-dotenv la meme chose pour les autre
        'debug':True,
        'host':"0.0.0.0"
    }
    app.run(**args)