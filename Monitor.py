from datetime import datetime, timezone
import aiohttp
import aiosqlite
import os
from calendar import monthrange
import asyncio

file_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(file_path, 'uptime.db')
db_lock = asyncio.Lock()

async def get_db_connection():
    conn = await aiosqlite.connect(db_path)
    conn.row_factory = aiosqlite.Row  
    return conn

class Monitor():
    def __init__(self,url, service_name ,interval,timeout, allow_redirect,group):
        self.last_served = datetime.now(timezone.utc).isoformat()
        self.url = url
        self.interval = interval
        self.timeout = timeout
        self.allow_redirect = allow_redirect
        self.running = True
        self.service_name = service_name
        self.group = group 
        self.conn = None
        
    
    async def ping(self,session):
            try:
                async with session.get(self.url, timeout=self.timeout,allow_redirects=self.allow_redirect) as resp:
                    
                    if resp.ok == True:
                        return 1
                    else:
                        return 0
            except Exception:
                return 0


    async def update_hour_info(self):
        min = datetime.now(timezone.utc).minute//2
        
        result = [0,[]]

        cursor = await self.conn.execute('SELECT DISTINCT success, all_requests  FROM monitors WHERE service_name = ?', (self.service_name,))
        record = await cursor.fetchone()
        
        result[0] = record["success"] / record["all_requests"] if record["all_requests"]!=0 else 1

 
        
        cursor = await self.conn.execute('SELECT * FROM checks WHERE url = ? AND timestamp>? ORDER BY timestamp DESC LIMIT 31;', (self.url,self.last_served))
        record = await cursor.fetchall()
        for e in record:
            result[1].append(e)

        self.last_served =result[1][0]["timestamp"] if len(result[1])>0 else datetime.now(timezone.utc).isoformat()

        for i in range(len(result[1])):
            result[1][i] =  dict(result[1][i])

        return result


    async def get_hour_info(self):

        min = datetime.now(timezone.utc).minute//2
        
        result = [0,[]]

        cursor = await self.conn.execute('SELECT DISTINCT success, all_requests  FROM monitors WHERE service_name = ?', (self.service_name,))
        record = await cursor.fetchone()
        
        result[0] = record["success"] / record["all_requests"] if record["all_requests"]!=0 else 1

        cursor = await self.conn.execute('SELECT * FROM checks WHERE url = ? ORDER BY timestamp DESC LIMIT 31;', (self.url,))
        record = await cursor.fetchall()
        for e in record:
            result[1].append(e)


        stv = 0
        if len(result[1])>0:
            stv = result[1][len(result[1])-1]["min"]-1
        else:
            stv = min-1

        if stv <1:
            stv = min
        
        while len(result[1])<30:
            result[1].append({"min": stv,"url": self.url,"timestamp": datetime.now(timezone.utc).isoformat(), "status":-1, "all_requests":0, "success":0})
            stv-=1
            if stv <1:
                stv = min

        for i in range(len(result[1])):
            result[1][i] =  dict(result[1][i])

        self.last_served =result[1][0]["timestamp"] if len(result[1])>0 else datetime.now(timezone.utc).isoformat()


        return result
    

    async def change_stat(self,min,st):
        async with db_lock:
            await self.conn.execute(
                """
                UPDATE checks
                SET all_requests = 0, success=0,status=0
                WHERE url = ? AND min = ?  AND ABS(strftime('%s', 'now') - strftime('%s', timestamp))>60;
                """, (self.url,min)

            )
            await self.conn.commit()
            await self.conn.execute('''
            INSERT INTO checks (min, url, timestamp,status, all_requests, success,service_name)
                VALUES (?, ?, ?,0, 0, 0,?)
                ON CONFLICT(min, url,service_name) DO UPDATE SET
                    all_requests = COALESCE(checks.all_requests, 0) + 1,
                    success = COALESCE(checks.success, 0) + ?,
                    timestamp = ?,
                    status = COALESCE(?, 0)
            ''', (min,self.url, datetime.now(timezone.utc).isoformat(), self.service_name, st,datetime.now(timezone.utc).isoformat(),st))
            await self.conn.commit()
            await self.conn.execute('''
            INSERT INTO monitors (url, service_name,interval,timeout,allow_redirect,success,all_requests,h24timestamp, mgroup)
                VALUES (?, ?, ?, ?, ?, 0, 0, ?,?)
                ON CONFLICT(url,service_name) DO UPDATE SET
                    all_requests = COALESCE(monitors.all_requests, 0) + 1,
                    success = COALESCE(monitors.success, 0) + ?,
                    h24timestamp = h24timestamp
            ''', ( self.url, self.service_name,self.interval,self.timeout,self.allow_redirect,datetime.now(timezone.utc).isoformat(), self.group,st))

            await self.conn.commit()

            await self.conn.execute(
                """
                UPDATE monitors
                SET all_requests = 0, success=0, h24timestamp = ?
                WHERE url = ?  AND ABS(strftime('%s', 'now') - strftime('%s', h24timestamp))>=86400;
                """, (datetime.now(timezone.utc).isoformat(),self.url)

            )
            await self.conn.commit()



    async def stop(self):
        self.running = False

    async def run(self):
        try:
            self.conn.close()
        except Exception:
            pass
        self.conn = await get_db_connection()

        
        await self.conn.execute('''
        CREATE TABLE IF NOT EXISTS checks (
            min INTEGER NOT NULL,
            url TEXT NOT NULL,
            timestamp TEXT NOT NULL,              
            status INTEGER NOT NULL,                                      
            all_requests INTEGER,                            
            success INTEGER,
            service_name TEXT,
            PRIMARY KEY (min, url,service_name)                       
        )
        ''')
    #    cursor.execute('DROP TABLE IF EXISTS monitors')
     #   self.conn.commit()

        await self.conn.execute('''
        CREATE TABLE IF NOT EXISTS monitors (
            url TEXT NOT NULL UNIQUE,   
            service_name TEXT UNIQUE,
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

        await self.conn.commit()


        self.running= True
        connector = aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)

        async with aiohttp.ClientSession(connector=connector) as session:
            while self.running:
                st = await self.ping(session)
                await self.change_stat(datetime.now(timezone.utc).minute // 2, st)
                await asyncio.sleep(self.interval)
       

        
        await self.conn.close()




