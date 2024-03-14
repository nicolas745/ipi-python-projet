#!.venv/bin/python3
from flask import Flask, render_template , request, session, g
import html
from hashlib import pbkdf2_hmac
import sqlite3
from enum import Enum
import os
import inspect
from threading import local
class env(Enum):
    USER="pseudo"
    PASSWD="passwd"
    INDEX="index.html"
    REGISTER="register.html"
    OKREGISTER = "le user {} a été enrgistré"
    MESSAGEREGISTER = "messageregister"
    LOGIN="login.html"
    ERROR404 ="404.html"
class sql:
    USER = "pseudo"

    def __init__(self, namefile: str) -> None:
        self._local = local()  # Crée un objet local pour stocker la connexion par thread
        self._local.conn = sqlite3.connect(namefile)
        cursor = self._local.conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {env.PASSWD.value} TEXT,
                {env.USER.value} TEXT
            );
        ''')
        cursor.close()
        self._local.conn.commit()

    def _get_conn(self):
        if not hasattr(self._local, 'conn') or not self._local.conn:
            self._local.conn = sqlite3.connect("database.db")
        return self._local.conn

    def ischeckuser(self, user, passwd):
        cursor = self._get_conn().cursor()
        res = cursor.execute(f"""
                SELECT * 
                FROM user 
                WHERE {env.USER.value}=? AND {env.PASSWD.value}=?
            """, (user, passwd))
        cursor.close()
        return res.rowcount != 0

    def adduser(self, user, passwd):
        cursor = self._get_conn().cursor()
        cursor.execute(f"""
            INSERT INTO user ({env.USER.value}, {env.PASSWD.value}) 
            VALUES (?, ?)
        """, (user, passwd))
        self._get_conn().commit()
        cursor.close()

class web():
    def __init__(self,app:Flask) -> None:
        @app.before_request
        def before_request():
            g.varible = {
                "message":{},
                "page":env.ERROR404.value
            }
    def render(self,**args):
        args['env'] = {}
        for key in env._member_map_:
            args['env'][key] =env[key].value
        return render_template("index.html",**args)
class UnauthPageHandler(web):
    def __init__(self,app:Flask) -> None:
        self.sql = sql("database.db")
        @app.get("/")
        def index():
            g.varible['page'] = env.INDEX.value
            return self.render(**g.varible)
        
        @app.post("/")
        def connect():
            g.varible['page'] = env.INDEX.value
            return self.render(**g.varible)
        
        @app.get("/"+env.REGISTER.value)
        def getregister():
            g.varible['page'] = env.REGISTER.value
            return self.render(**g.varible)
        @app.post("/"+env.REGISTER.value)
        def postregister():
            g.varible['page'] = env.REGISTER.value
            if request.form.get("submit"):
                user = request.form.get(env.USER.value)
                salt = salt = os.urandom(16) 
                passwd = pbkdf2_hmac('sha256', request.form.get(env.PASSWD.value).encode(), salt, 100000, 32)
                if user and passwd:
                    self.sql.adduser(
                        user.encode(),
                        passwd.hex()
                    )
                    g.varible['message'][env.MESSAGEREGISTER.value] = html.escape(env.OKREGISTER.value.format(user))
            return self.render(**g.varible)
        @app.get("/"+env.LOGIN.value)
        def getlogin():
            return self.render(**g.varible)
        @app.post("/"+env.LOGIN.value)
        def postlogin():
            return self.render(**g.varible)
        @app.errorhandler(404)
        def page_not_found(e):
            return self.render(**g.varible), 404
class authHandler(web):
    def __init__(self, app: Flask) -> None: 
        super().__init__(app)
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
