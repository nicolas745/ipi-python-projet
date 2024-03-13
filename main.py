#!.venv/bin/python3
from flask import Flask, render_template
from hashlib import sha256
import sqlite3
from enum import Enum
import inspect

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
        cusor.execute(f'''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {env.PASSWD.value} TEXT,
                {env.USER.value} TEXT
            );
        ''')
        cusor.close()
        self.conn.commit()
    def ischeckuser(self,user,passwd):
        cursor=self.conn.cursor()
        res=cursor.execute(f"""
                SELECT * 
                FROM user 
                WHERE {env.USER.value}=? AND {env.PASSWD.value}=?
            """,(user,passwd))
        cursor.close()
        return res.rowcount!=0
    def adduser(self, user, passwd):
        cursor = self.conn.cursor()
        cursor.execute(f"""
            INSERT INTO user ({env.USER.value,}, {env.PASSWD.value}) 
            VALUES (?, ?)
        """, (user, passwd))
        self.conn.commit()
        cursor.close()

class web():
    def __init__(self,app:Flask) -> None:
        pass
    def render(self,**args):
        return render_template("index.html",**args)
class UnauthPageHandler(web):
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

#UnauthPageHandler(app)
if __name__ == '__main__':
    app = Flask(__name__)
    global_data = globals().copy()
    for key, value in global_data.items():
        if inspect.isclass(value):
            if(issubclass(value,web)):
                value(app)

    args = {
        'port':8080,  #comme ameloration je peut utlise os.getenv('port') mais il faut charger le fichier lib python-dotenv la meme chose pour les autre
        'debug':True,
        'host':"0.0.0.0"
    }
    app.run(**args)