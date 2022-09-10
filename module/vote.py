import datetime


# With the user login 
# class Vote:
#     def __init__(self, db) -> None:
#         self.db  =  db 
#     async def check(self, votingrestiction:str, userid:str ,request:Request ,pollid:str, macaddr:str):
#         if votingrestiction=="One vote browser session":
#             if  await self.db['browser_collection'].find_one({"userid":userid, "pollid":pollid}):
#                 return False
#             await self.db['browser_collection'].insert_one({"userid":userid, "pollid":pollid, "date":datetime.datetime.utcnow()})
#         if votingrestiction=="One vote per IP address":
#             if await self.db['ip_collection'].find_one({"userid":userid, "pollid":pollid, "macaddress":macaddr}):
#                 return False
#             await self.db['ip_collection'].insert_one({"userid":userid, "pollid":pollid, "macaddress":macaddr})
#         return True 


# Without user login 
class Vote:
    def __init__(self, db) -> None:
        self.db  =  db 
    async def check(self, votingrestiction:str,pollid:str, macaddr:str):
        if votingrestiction=="One vote browser session":
            if  await self.db['browser_collection'].find_one({"macaddress":macaddr, "pollid":pollid}):
                return False
            await self.db['browser_collection'].insert_one({"macaddress":macaddr, "pollid":pollid, "date":datetime.datetime.utcnow()})
        if votingrestiction=="One vote per IP address":
            if await self.db['ip_collection'].find_one({ "pollid":pollid, "macaddress":macaddr}):
                return False
            await self.db['ip_collection'].insert_one({"pollid":pollid, "macaddress":macaddr})
        return True 