from quart import Quart, request, jsonify, render_template, redirect, session
from quart import url_for 
from datetime import datetime
import time
import aiosqlite
import os
import asyncio
from Monitor import Monitor 
import bcrypt
from functools import wraps
import markdown
from werkzeug.utils import secure_filename;
import logging
logging.getLogger('asyncio').setLevel(logging.ERROR)

rate_limits = {}   
RATE = 15          
WINDOW = 5

app = Quart(__name__)  
app.config.update({
    "SESSION_COOKIE_SAMESITE": "Strict",
    "SESSION_COOKIE_SECURE": True,   
})

file_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(file_path, 'uptime.db')

services = [] 
urls = []
names=[]

timezone = datetime.tzname(datetime.now())

user_exists = False
title = "Uptime"
md=""
image = "favicon.png"

ALLOWED = {"png", "jpg", "jpeg", "webp", "ico"}
app.config['MAX_CONTENT_LENGTH'] = 50 *1000 * 1024

image_path =os.path.join(os.path.dirname(os.path.abspath(__file__)).replace("\\","/"),"static/img")


async def init_db():
    async with aiosqlite.connect(db_path) as cursor:
        await cursor.execute("PRAGMA journal_mode=WAL;")
        await cursor.commit()
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                    login TEXT NOT NULL UNIQUE,                                      
                    password TEXT NOT NULL,
                    PRIMARY KEY (login)                       
                )
            ''')

        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS server (
                    title TEXT NOT NULL UNIQUE DEFAULT "Uptime",                                      
                    md TEXT,
                    image TEXT
                    
                )
            ''')

        await cursor.execute('''
            INSERT INTO server (md, image)
            SELECT '', 'favicon.png'
            WHERE NOT EXISTS (SELECT 1 FROM server);

            ''')


        await cursor.commit()

def r2rgb(x):
    if x == -1:
        return (128, 128, 128)
    if (x <= 0.5):
        r = 0.9
        g = 1.4 * x
        b = 0.0
    else:
        r = 1.8 * (1 - x)
        g = 0.7
        b = 0.0
        
    r255 = round(r * 255)
    g255 = round(g * 255)
    b255 = round(b * 255)
    return (r255, g255, b255)
     
def login_required(f): 
    @wraps(f)
    async def decorated(*args, **kwargs):  
        if 'login' not in session:
            return redirect(url_for("render_login"))
        result = await f(*args, **kwargs) 
        return result
    return decorated

def user_required(f): 
    @wraps(f)
    async def decorated(*args, **kwargs):  
        global user_exists
        if not user_exists:
            return redirect(url_for("render_reg"))
        result = await f(*args, **kwargs) 
        return result
    return decorated

@app.route("/")
@user_required
async def index(): 
    clname = "mdblock" if md!="" else "dispnone"
    min_h = 50 if md!="" else 70
    return await render_template("index.html", path=url_for('static',filename=f"img/{image}"), title=title, md= markdown.markdown(md),classname=clname,min_h=min_h) 

@app.route("/admin/")
@login_required
@user_required
async def admin(): 
    return await render_template("admin.html",title=title,md=md, path=url_for('static',filename=f"img/{image}")) 

@app.route("/admin/registration")
async def render_reg(): 
    if user_exists:
        return redirect(url_for('render_login'))
    return await render_template("reg.html") 

@user_required
@app.route("/admin/login")
async def render_login(): 
    return await render_template("login.html") 

@app.route("/api/registrate",methods=['POST'])
async def registrate(): 
        global user_exists
        data = await request.get_json()
        login=data['login']
        password=data['password']
               
        pwd_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        async with aiosqlite.connect(db_path) as conn:  
            try:
                await conn.execute('INSERT INTO users (login, password) VALUES (?, ?)', (login, pwd_hash))
                await conn.commit()
            except aiosqlite.IntegrityError:  
                return jsonify({"error": "Login exists"}), 409
        
        session['login'] = login
        session.permanent = True
        user_exists = True
        
        return url_for("admin")
 
@app.route("/api/logout",methods=['GET'])
async def logout(): 
    session.clear()
    return redirect(url_for("render_login"))

@app.route("/api/login",methods=['POST'])
async def login(): 

    data = await request.get_json()

    login=data['login']
    password=data['password']
               

    async with aiosqlite.connect(db_path) as conn: 
            async with conn.execute('SELECT password FROM users WHERE login = ?', (login,)) as cursor:
                result = await cursor.fetchone()
                if not result: 
                    return jsonify({"error": "Not found"}), 400
                stored_hash = result[0].encode('utf-8')
    
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        session['login'] = login
        session.permanent = True
        return url_for("admin")
    else:
        return "400"


@app.route("/api/hourinfo")
async def get_hour_info():  
    res = {}
    groups = {} 
    for service in services:
        groups.setdefault(service.group, []).append(service)


    for group in groups:
        res[group] = {}
        tasks = [service.get_hour_info() for service in groups[group]]
        results = await asyncio.gather(*tasks)  

        for i, r in enumerate(results):
            hourinfo = []
            hourinfo.append({"uptime": round(r[0]*100, 1), "rgb": r2rgb(r[0])})
            for day_info in r[1]:
                uptime = day_info["success"] / day_info["all_requests"] if day_info["all_requests"] != 0 else -1
                hourinfo.append(dict({
                    "uptime": uptime if uptime!=-1 else 0,
                    "rgb": r2rgb(uptime),
                    "time": datetime.fromisoformat(day_info["timestamp"]).astimezone(timezone).time().strftime('%H:%M') if day_info["status"] !=-1 else ""
                }))

            res[group][groups[group][i].service_name] = hourinfo     
            
    return jsonify(res)

@app.route("/api/updhourinfo")
async def update_hour_info(): 
    res = {}
    groups = {} 
    for service in services:
        groups.setdefault(service.group, []).append(service)


    for group in groups:
        res[group] = {}
        tasks = [service.update_hour_info() for service in groups[group]]
        results = await asyncio.gather(*tasks)  

        for i, r in enumerate(results):
            hourinfo = []
            hourinfo.append({"uptime": round(r[0]*100, 1), "rgb": r2rgb(r[0])})
            for day_info in r[1]:
                uptime = day_info["success"] / day_info["all_requests"] if day_info["all_requests"] != 0 else 1
                hourinfo.append(dict({
                    "uptime": round(uptime, 1),
                    "rgb": r2rgb(uptime),
                    "time": datetime.fromisoformat(day_info["timestamp"]).astimezone(timezone).time().strftime('%H:%M')
                }))

            res[group][groups[group][i].service_name] = hourinfo        

    return jsonify(res)

@login_required
@app.route("/api/changemonitor", methods=['POST'])
async def changemonitor():
    global services
    data = await request.get_json()   
 
    await deletemonitor(int(data["idx"]))
    services.append(Monitor(
                url=data['url'],
                service_name=data['name'],
                interval=int(data['interval']),
                timeout=int(data['timeout']),
                allow_redirect=bool(data['redirect']),  
                group=data["group"]
            ))


    coro = services[-1].run()
    task = asyncio.create_task(coro)

    return await get_monitors()

@login_required
@app.route("/api/createMonitor", methods=['POST'])
async def createmonitor():
    global services
    data = await request.get_json()   
    _interval = int(data['interval'])
    if _interval<3:
        _interval=3
    if not data['url'] in urls and not data['name'] in names:
        services.append(Monitor(
                    url=data['url'],
                    service_name=data['name'],
                    interval=_interval,
                    timeout=int(data['timeout']),
                    allow_redirect=bool(data['redirect']),  
                    group=data["group"]
                ))

        for service in services:
            urls.append(service.url)
            names.append(service.service_name)

        coro = services[-1].run()
        task = asyncio.create_task(coro)

    return await get_monitors()
    
        

@login_required
@app.route("/api/deletemonitor", methods=['POST'])
async def delmonitor():
    global services
    data = await request.get_json()   
 
    await deletemonitor(int(data["idx"]))

    return await get_monitors()

async def deletemonitor(idx):
    global services

    name = services[idx].service_name
    print(name)
    async with aiosqlite.connect(db_path) as cursor:

        await cursor.execute('''
            DELETE FROM monitors WHERE service_name=?                     
            ''', (name,))

        await cursor.commit()

        await cursor.execute('''
            DELETE FROM checks WHERE service_name=?                     
            ''', (name,))

        await cursor.commit()

    await services[idx].stop()

    del services[idx]

@app.route("/api/getmonitors")
async def get_monitors():
    try:
        global services
        res = {}
        groups = {} 
        i=0
        for service in services:
            groups.setdefault(service.group, []).append([service,i])
            i+=1

        for group in groups:
            for service in groups[group]:
                res[service[0].service_name] = {"url": service[0].url, "interval": service[0].interval,"timeout":service[0].timeout, "group":service[0].group, "allow_redirect": service[0].allow_redirect, "index": service[1] }
        
        return jsonify(res)
    except Exception as ex:
        return str(ex)

@login_required
@app.route("/api/setimage", methods=['POST'])
async def setimage():
    global image
    global title
    global image_path
    f = await request.files
    
    file = f.get("file")
    if file:
        ext = file.filename.rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED:
            return "Bad file", 400
        os.remove(os.path.join(image_path,image))
        image =secure_filename(file.filename)
        print(image_path, os.path.join(image_path,image))
        await file.save(os.path.join(image_path,image))
        async with aiosqlite.connect(db_path) as conn:
            conn.row_factory = aiosqlite.Row  
            cursor = await conn.cursor()
            await cursor.execute(
            """
            UPDATE server
            SET image = ?
            WHERE title = ?;
            """, (image, title)

            )
            await conn.commit()


    return "200"

@login_required
@app.route("/api/changeserverinfo",methods=['POST'])
async def changeserverinfo():
    global title
    global md
    data = await request.get_json()   
    
    md =(data["md"])

    async with aiosqlite.connect(db_path) as conn:
            conn.row_factory = aiosqlite.Row  
            cursor = await conn.cursor()
            await cursor.execute(
            """
            UPDATE server
            SET title = ?, md=?
            WHERE title = ?;
            """, ( data["title"],md, title)

            )
            await conn.commit()
    
    title = data["title"]
    
    return "200"


@app.before_serving
async def startup():
    global services

    global urls
    global names
    await init_db()

    async with aiosqlite.connect(db_path) as conn:
        conn.row_factory = aiosqlite.Row  
        cursor = await conn.cursor()

        global title
        global md
        global user_exists
        global image

        await cursor.execute("""
                SELECT * FROM users;
            """)
        record = await cursor.fetchall()
        if len(record)<1:
            user_exists = False
        else:
            user_exists = True

        await cursor.execute('''
        CREATE TABLE IF NOT EXISTS monitors (
            url TEXT NOT NULL,   
            service_name TEXT,
            interval REAL,
            timeout REAL,
            allow_redirect INTEGER,
            success INTEGER,
            all_requests INTEGER,
            h24timestamp TEXT NOT NULL, 
            mgroup TEXT NOT NULL,
            PRIMARY KEY (url,service_name)                       
        )
        ''')

        await conn.commit()

        await cursor.execute("""
            SELECT * FROM server;
        """)
        record = await cursor.fetchone()
        title = record["title"]
        md=record["md"]
        image=record["image"]


        await cursor.execute("""
            SELECT DISTINCT url, service_name, interval, timeout, allow_redirect, mgroup FROM monitors;
        """)
        record = await cursor.fetchall()
    for el in record:
        services.append(Monitor(el["url"], el["service_name"], int(el["interval"]), int(el["timeout"]), bool(el["allow_redirect"]), el["mgroup"]))
    await conn.close() 

    for service in services:
        await service.stop()  

    for service in services:
        urls.append(service.url)
        names.append(service.service_name)

    for service in services:
        coro = service.run() 
        task = asyncio.create_task(coro) 

@app.before_request
async def rate_limit():
    ip = request.headers.get("X-Real-IP", request.remote_addr)
    now = time.time()

    bucket = rate_limits.get(ip, [])
    bucket = [t for t in bucket if now - t < WINDOW]

    if len(bucket) >= RATE:
        return jsonify({"error": "Too Many Requests"}), 429

    bucket.append(now)
    rate_limits[ip] = bucket

@app.errorhandler(404)
async def redir(err):
    return redirect(url_for("index"))

if __name__ == '__main__':
    try:
        with open(os.path.join(file_path,".SECRETKEY"),"rb") as f:
            app.secret_key = f.read()
    except FileNotFoundError:
        with open(os.path.join(file_path,".SECRETKEY"),"wb") as f:
            app.secret_key = os.urandom(32)
            f.write(app.secret_key)
    app.run(debug=True, host='localhost', port=5000)