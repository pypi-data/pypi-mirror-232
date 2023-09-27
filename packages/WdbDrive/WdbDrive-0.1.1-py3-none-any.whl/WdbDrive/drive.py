import aiohttp
import hashlib
import json
import time
import base64


class Wdb:
    host = ""
    key = ""

    def __init__(self, host, key):
        self.host = host
        self.key = key

    async def CreateObj(self, key: str, data: str, categories: [str]):
        tm = await self.ctime()
        sg = await self.sign("%s%d%s%s"%(self.key, tm, key, data))
        return await self.post_data('/wdb/api/create', {
            'key': key,
            'categories': categories,
            'content': data,
            'time': tm,
            'sg': sg
        })

    async def UpdateObj(self, key: str, data: str):
        tm = await self.ctime()
        sg = await self.sign("%s%d%s%s"%(self.key, tm, key, data))
        return await self.post_data('/wdb/api/update', {
            'key': key,
            'content': data,
            'time': tm,
            'sg': sg
        })

    async def GetObj(self, key: str):
        tm = await self.ctime()
        sg = await self.sign("%s%d%s" % (self.key, tm, key))
        return await self.get_data('/wdb/api/get?key=' + key + '&time=' + str(tm) + '&sg=' + sg)

    async def DelObj(self, key: str):
        tm = await self.ctime()
        sg = await self.sign("%s%d%s"%(self.key, tm, key))
        return await self.get_data('/wdb/api/del?key=' + key + '&time=' + str(tm) + '&sg=' + sg)

    async def ListObj(self, category: str, offset: int, limit: int, order: str):
        tm = await self.ctime()
        sg = await self.sign("%s%s%d"%(self.key, category, tm))
        rsp = await self.get_data('/wdb/api/list?category=' + category + '&offset=' + str(offset) + '&limit=' + str(limit) + '&order=' + order + '&time=' + str(tm) + '&sg=' + sg)
        if rsp['code'] != 200:
            return {'code': 400, 'msg': rsp['msg']}
        clist = json.loads(rsp['data'])
        return {'code': 200, 'total':clist['total'], 'list': clist['list']}

    async def TransBegin(self, lock_ids: [str]):
        tm = await self.ctime()
        sg = await self.sign("%s%d"%(self.key, tm))
        return await self.post_data('/wdb/api/trans/begin', {
            'keys': lock_ids,
            'time': tm,
            'sg': sg
        })
    
    async def TransCreateObj(self, tsid: str, key: str, data: str, categories: [str]):
        tm = await self.ctime()
        sg = await self.sign("%s%d%s%s%s"%(self.key, tm, key, data, tsid))
        return await self.post_data('/wdb/api/trans/create', {
            'tsid': tsid,
            'key': key,
            'categories': categories,
            'content': data,
            'time': tm,
            'sg': sg
        })
    
    async def TransUpdateObj(self, tsid: str, key: str, data: str):
        tm = await self.ctime()
        sg = await self.sign("%s%d%s%s%s"%(self.key, tm, key, data, tsid))
        return await self.post_data('/wdb/api/trans/update', {
            'tsid': tsid,
            'key': key,
            'content': data,
            'time': tm,
            'sg': sg
        })
    
    async def TransGet(self, tsid: str, key: str):
        tm = await self.ctime()
        sg = await self.sign("%s%d%s%s"%(self.key, tm, key, tsid))
        return await self.get_data('/wdb/api/trans/get?tsid=' + tsid + '&key=' + key + '&time=' + str(tm) + '&sg=' + sg)
    
    async def TransDelObj(self, tsid: str, key: str):
        tm = await self.ctime()
        sg = await self.sign("%s%d%s%s"%(self.key, tm, key, tsid))
        return await self.get_data('/wdb/api/trans/del?tsid=' + tsid + '&key=' + key + '&time=' + str(tm) + '&sg=' + sg)
    
    async def TransCommit(self, tsid: str):
        tm = await self.ctime()
        sg = await self.sign("%s%d%s"%(self.key, tm, tsid))
        return await self.post_data('/wdb/api/trans/commit', {
            'tsid': tsid,
            'time': tm,
            'sg': sg
        })
    
    async def TransRollBack(self, tsid: str):
        tm = await self.ctime()
        sg = await self.sign("%s%d%s"%(self.key, tm, tsid))
        return await self.post_data('/wdb/api/trans/roll_back', {
            'tsid': tsid,
            'time': tm,
            'sg': sg
        })
    
    async def CreateIndex(self, indexkeys: [str], key: str, indexraw: [str]):
        tm = await self.ctime()
        sg = await self.sign("%s%d%s"%(self.key, tm, key))
        return await self.post_data('/wdb/api/index/create', {
            'indexkey': indexkeys,
            'key': key,
            'indexraw': indexraw,
            'time': tm,
            'sg': sg
        })
    
    async def UpdateIndex(self, oindexkeys: [str], cindexkeys: [str], key: str, indexraw: [str]):
        tm = await self.ctime()
        sg = await self.sign("%s%d%s"%(self.key, tm, key))
        return await self.post_data('/wdb/api/index/update', {
            'oindexkey': oindexkeys,
            'cindexkey': cindexkeys,
            'key': key,
            'indexraw': indexraw,
            'time': tm,
            'sg': sg
        })
    
    async def DelIndex(self, indexkeys: [str], key: str):
        tm = await self.ctime()
        sg = await self.sign("%s%d%s"%(self.key, tm, key))
        return await self.post_data('/wdb/api/index/del', {
            'indexkey': indexkeys,
            'key': key,
            'time': tm,
            'sg': sg
        })
    
    async def ListIndex(self, indexkey: str, condition: str, offset: int, limit: int, order: str):
        tm = await self.ctime()
        sg = await self.sign("%s%s%d"%(self.key, indexkey, tm))
        rsp = await self.post_data('/wdb/api/index/list', {
            'indexkey': indexkey,
            'condition': condition,
            'offset': offset,
            'limit': limit,
            'order': order,
            'time': tm,
            'sg': sg
        })
        if rsp['code'] != 200:
            return {'code': 400, 'msg': rsp['msg']}
        clist = json.loads(rsp['data'])
        return {'code': 200, 'total': clist['total'], 'list': clist['list']}

    async def CreateRawData(self, key: str, raw: bytes, categories: [str]):
        content = base64.b64encode(raw).decode()
        tm = await self.ctime()
        sg = await self.sign("%s%d%s%s"%(self.key, tm, key, content))
        return await self.post_data('/wdb/api/create_raw', {
            'key': key,
            'categories': categories,
            'content': content,
            'time': tm,
            'sg': sg
        })

    async def GetRawData(self, key: str):
        tm = await self.ctime()
        sg = await self.sign("%s%d%s"%(self.key, tm, key))
        rsp = await self.get_data('/wdb/api/get_raw?key=' + key + '&time=' + str(tm) + '&sg=' + sg)
        if rsp['code'] == 200:
            data = base64.b64decode(rsp['data'])
            return {'code': 200, 'raw': data}
        else:
            return {'code': 400, 'msg': rsp['msg']}

    async def GetRangeData(self, key: str, offset: int, limit: int):
        tm = await self.ctime()
        sg = await self.sign("%s%d%s"%(self.key, tm, key))
        rsp = await self.get_data('/wdb/api/get_range?key=' + key + '&offset=' + str(offset) + '&limit=' + str(limit) + '&time=' + str(tm) + '&sg=' + sg)
        if rsp['code'] == 200:
            rdata = json.loads(rsp['data'])
            data = base64.b64decode(rdata['data'])
            return {'code': 200, 'all_size': rdata['all_size'], 'raw': data}
        else:
            return {'code': 400, 'msg': rsp['msg']}

    async def UploadByPath(self, path: str, key: str, categories: [str]):
        tm = await self.ctime()
        sg = await self.sign("%s%d%s"%(self.key, tm, key))
        return await self.post_data('/wdb/api/upload', {
            'path': path,
            'key': key,
            'categories': categories,
            'time': tm,
            'sg': sg
        })
    
    async def DownToPath(self, path: str, key: str):
        tm = await self.ctime()
        sg = await self.sign("%s%d%s"%(self.key, tm, key))
        return await self.post_data('/wdb/api/down', {
            'path': path,
            'key': key,
            'time': tm,
            'sg': sg
        })
    
    async def ctime(self):
        return int(time.time())

    async def sign(self, text):
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    async def get_data(self, path):
        url = self.host + path
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        rsp = await response.json()
                        return rsp
                    else:
                        return {'code':500, 'msg': response.text()}
            except aiohttp.ClientConnectorError as  e:
                return {'code':500, 'msg': str(e)}

    async def post_data(self, path, body):
        url = self.host + path
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json = body) as response:
                    if response.status == 200:
                        rsp = await response.json()
                        return rsp
                    else:
                        return {'code':500, 'msg': response.text()}
            except aiohttp.ClientConnectorError as  e:
                return {'code':500, 'msg': str(e)}
