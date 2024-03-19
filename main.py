#!.venv/bin/python3
from flask import Flask, render_template , request, session, g , redirect
import html
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from enum import Enum
import os
import inspect
from threading import local
class env(Enum):
    USER="pseudo"
    FORUMTITRE="titre"
    FORUMMESSAGE="message"
    FORUMIDUSER="id_pseudo"
    FORUMTIME="time"
    PASSWD="passwd"
    INDEX="index.html"
    WIKI="wiki.html"
    REGISTER="register.html"
    OKREGISTER = "le user {} a été enrgistré"
    MESSAGEREGISTER = "messageregister"
    LOGIN="login.html"
    ERROR404 ="404.html"
class sql:
    def __init__(self, namefile: str) -> None:
        self._local = local()
        self._local.conn = sqlite3.connect(namefile)
        cursor = self._local.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {} TEXT,
                {} TEXT
            );
        '''.format(env.PASSWD.value,env.USER.value))
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forum (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {} TEXT,
                {} TEXT,
                {} INT,
                {} INT,
                FOREIGN KEY ({}) REFERENCES user(id)
            );
        '''.format(env.FORUMTITRE.value,env.FORUMMESSAGE.value,env.FORUMIDUSER.value,env.FORUMTIME.value,env.FORUMIDUSER.value))
        cursor.close()
        self._local.conn.commit()
    def _get_conn(self):
        if not hasattr(self._local, 'conn') or not self._local.conn:
            self._local.conn = sqlite3.connect("database.db")
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def getpasswd(self, user) -> bool:
        cursor = self._get_conn().cursor()
        cursor.execute(f"""
                SELECT * 
                FROM user 
                WHERE `pseudo`='a';
            """)
        res=cursor.fetchone()
        print()
        cursor.close()
        return  res[env.PASSWD.value]

    def adduser(self, user, passwd):
        cursor = self._get_conn().cursor()
        cursor.execute(f"""
            INSERT INTO user (`{env.USER.value}`, `{env.PASSWD.value}`) 
            VALUES (?, ?)
        """, (user, passwd))
        self._get_conn().commit()
        cursor.close()

class web():
    def __init__(self,app:Flask) -> None:
        @app.before_request
        def before_request():
            self.before_request()
    def before_request(self):
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
        super().__init__(app)
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
                passwd = generate_password_hash(request.form.get(env.PASSWD.value))
                if user and passwd:
                    self.sql.adduser(
                        user,
                        passwd
                    )
                    g.varible['message'][env.MESSAGEREGISTER.value] = html.escape(env.OKREGISTER.value.format(user))
            return self.render(**g.varible)
        @app.get("/"+env.LOGIN.value)
        def getlogin():
            g.varible['page'] = env.LOGIN.value
            return self.render(**g.varible)
        @app.post("/"+env.LOGIN.value)
        def postlogin():
            g.varible['page'] = env.LOGIN.value
            if request.form.get("submit"):
                user = request.form.get(env.USER.value)
                passwd = request.form.get(env.PASSWD.value)
                if user and request.form.get(env.PASSWD.value):
                    passwd_hash=self.sql.getpasswd(user)
                    if check_password_hash(passwd_hash, passwd):
                        session[env.USER.value] = user
                        return redirect("/membre")
            return self.render(**g.varible)
        @app.errorhandler(404)
        def page_not_found(e):
            return self.render(**g.varible), 404
class authHandler(web):
    def __init__(self, app: Flask) -> None: 
        @app.get("/membre")
        def membre():
            g.varible['page'] = env.LOGIN.value
            return self.render(**g.varible)
if __name__ == '__main__':
    app = Flask(__name__)
    app.secret_key  = os.urandom(24)
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
