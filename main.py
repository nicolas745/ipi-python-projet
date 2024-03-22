#!/usr/bin/env python
from flask import Flask, render_template , request, session, g , redirect
import html
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from enum import Enum
import os
import time
import inspect
from threading import local
class env(Enum):
    USER="pseudo"
    FORUMTITRE="titre"
    FORUMMESSAGE="message"
    FORUMIDUSER="id_pseudo"
    FORUMTIME="time"
    PASSWD="passwd"
    FORUM = "forum.html"
    INDEX="index.html"
    FORUMS="forums.html"
    ACCOUNT="account.html"
    LOGOUT="logout.html"
    WIKI="wiki.html"
    REGISTER="register.html"
    OKREGISTER = "le user {} a été enrgistré"
    MESSAGEREGISTER = "messageregister"
    LOGIN="login.html"
    ERROR404 ="404.html"
class sql:
    def __init__(self, namefile: str="database.db") -> None:
        self.namefile = namefile
        con = self._get_conn()
        cursor = con.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS user ( id INTEGER PRIMARY KEY AUTOINCREMENT, {env.PASSWD.value} TEXT, {env.USER.value} TEXT);")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS forum ( id INTEGER PRIMARY KEY AUTOINCREMENT, {env.FORUMTITRE.value} TEXT, {env.FORUMMESSAGE.value} TEXT, {env.FORUMIDUSER.value} INT, {env.FORUMTIME.value} INT, FOREIGN KEY ({env.FORUMIDUSER.value}) REFERENCES user(id) );")
        con.commit()
        cursor.close()
        con.close()
    def listforum(self,per_page,offset):
        con = self._get_conn()
        cursor = con.cursor()
        cursor.execute(f'SELECT DISTINCT {env.FORUMTITRE.value} FROM forum ORDER BY id DESC LIMIT ? OFFSET ?', (per_page,offset))
        forum = cursor.fetchall()
        cursor.close()
        con.close()
        return forum
    def _get_conn(self):
        conn = sqlite3.connect(self.namefile)
        conn.row_factory = sqlite3.Row
        return conn
    def getiduser(self,user):
        con = self._get_conn()
        cursor = con.cursor()
        cursor.execute(f" SELECT id  FROM user  WHERE `{env.USER.value}`=?;",(user,))
        res=cursor.fetchone()
        cursor.close()
        con.close()
        if(not res):
            return None
        return  res["id"]
    def getpasswd(self, user) -> bool:
        con = self._get_conn()
        cursor = con.cursor()
        cursor.execute(f" SELECT {env.PASSWD.value}  FROM user  WHERE `{env.USER.value}`=?;",(user,))
        res=cursor.fetchone()
        cursor.close()
        con.close()
        if(not res):
            return None
        return  res[env.PASSWD.value]
    def addforum(self,title,message):
        con = self._get_conn()
        cursor = con.cursor()
        cursor.execute(f"INSERT INTO forum ({env.FORUMTITRE.value}, {env.FORUMMESSAGE.value}, {env.FORUMIDUSER.value}, {env.FORUMTIME.value}) VALUES (?, ?, ?, ?)",(title, message, self.getiduser(session.get(env.USER.value)), time.time()))
        con.commit()
        cursor.close()
        con.close()
    def adduser(self, user, passwd):
        con = self._get_conn()
        cursor = con.cursor()
        cursor.execute(f"INSERT INTO user (`{env.USER.value}`, `{env.PASSWD.value}`) VALUES (?, ?)", (user, passwd))
        con.commit()
        cursor.close()
        con.close()
    def listmessage(self,title,per_page,offset):
        con = self._get_conn()
        cursor = con.cursor()
        cursor.execute(f'SELECT forum.*, user.{env.USER.value}  FROM forum JOIN user ON forum.{env.FORUMIDUSER.value} = user.id WHERE {env.FORUMTITRE.value}=? ORDER BY id ASC LIMIT ? OFFSET ?', (title,per_page,offset))
        message = cursor.fetchall()
        cursor.close()
        con.close()
        return message
        
class web():
    def __init__(self,app:Flask) -> None:
        self.sql = sql()
        @app.before_request
        def before_request():
            return self.before_request()
    def before_request(self):
        g.varible = {
            "message":{},
            "page":env.ERROR404.value,
            "args": request.args.to_dict()
            }
    def render(self,**args):
        args['env'] = {}
        for key in env._member_map_:
            args['env'][key] =env[key].value
        return render_template("index.html",**args)
class UnauthPageHandler(web):
    def __init__(self,app:Flask) -> None:
        super().__init__(app)
        @app.get("/")
        def index():
            if session.get(env.USER.value):
                return redirect("/"+env.ACCOUNT.value)
            g.varible['page'] = env.INDEX.value
            return self.render(**g.varible)
        @app.get("/"+env.REGISTER.value)
        def getregister():
            if session.get(env.USER.value):
                return redirect("/"+env.ACCOUNT.value)
            g.varible['page'] = env.REGISTER.value
            return self.render(**g.varible)
        @app.post("/"+env.REGISTER.value)
        def postregister():
            if session.get(env.USER.value):
                return redirect("/"+env.ACCOUNT.value)
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
            if session.get(env.USER.value):
                return redirect("/"+env.ACCOUNT.value)
            g.varible['page'] = env.LOGIN.value
            return self.render(**g.varible)
        @app.post("/"+env.LOGIN.value)
        def postlogin():
            if session.get(env.USER.value):
                return redirect("/"+env.ACCOUNT.value)
            g.varible['page'] = env.LOGIN.value
            if request.form.get("submit"):
                user = request.form.get(env.USER.value)
                passwd = request.form.get(env.PASSWD.value)
                if user and request.form.get(env.PASSWD.value):
                    passwd_hash=self.sql.getpasswd(user)
                    if(passwd_hash):
                        if check_password_hash(passwd_hash, passwd):
                            session[env.USER.value]= user
                            return redirect("/"+env.ACCOUNT.value)
            return self.render(**g.varible)
        @app.get("/forum/<title>/")
        def getforum(title):
            page = request.args.get('page', default=1, type=int)
            per_page = 10
            offset = (page - 1) * per_page
            g.varible['page'] = env.FORUM.value
            g.varible['forum'] = self.sql.listmessage(title,per_page,offset)
            return self.render(**g.varible)
        @app.get("/"+env.FORUMS.value)
        def forum():
            page = request.args.get('page', default=1, type=int)
            per_page = 10
            offset = (page - 1) * per_page
            g.varible['page'] = env.FORUMS.value
            g.varible['forums']=self.sql.listforum(per_page,offset)
            return self.render(**g.varible)
        @app.errorhandler(404)
        def page_not_found(e):
            return self.render(**g.varible), 404
class authHandler(web):
    def __init__(self, app: Flask) -> None: 
        super().__init__(app)
        @app.get("/"+env.LOGOUT.value)
        def logout():
            session.clear()
            return redirect("/")
        @app.route("/"+env.ACCOUNT.value,methods=["POST","GET"])
        def membre():
            if not session.get(env.USER.value):
                return redirect("/")
            g.varible['page'] = env.ACCOUNT.value
            return self.render(**g.varible)
        @app.post("/forum/<title>/")
        def postforum(title):
            if not session.get(env.USER.value):
                return redirect("")
            self.sendforum(title)
            page = request.args.get('page', default=1, type=int)
            per_page = 10
            offset = (page - 1) * per_page
            g.varible['page'] = env.FORUM.value
            g.varible['forum'] = self.sql.listmessage(title,per_page,offset)
            return self.render(**g.varible)
        @app.post("/"+env.FORUMS.value)
        def forums():
            if not session.get(env.USER.value):
                return redirect("")
            self.sendforum(request.form.get(env.FORUMTITRE.value))
            page = request.args.get('page', default=1, type=int)
            per_page = 10
            offset = (page - 1) * per_page
            g.varible['page'] = env.FORUMS.value
            g.varible['forums']=self.sql.listforum(per_page,offset)
            return self.render(**g.varible)
    def sendforum(self,title):
        if request.form.get("submit"):
            message = request.form.get(env.FORUMMESSAGE.value)
            if title and message:
                self.sql.addforum(title,message)
if __name__ == '__main__':
    app = Flask(__name__)
    app.secret_key  = os.urandom(24)
    global_data = globals().copy()
    for key, value in global_data.items():
        if inspect.isclass(value):
            if(issubclass(value,web)):
                if value.__name__ != "web":
                    value(app)
    args = {
        'port':8080,
        'debug':True,
        'host':"0.0.0.0"
    }
    app.run(**args)
