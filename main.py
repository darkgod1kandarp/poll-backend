from datetime import datetime
from itertools import count
import os
from sys import breakpointhook
from fastapi import FastAPI, Body, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import motor.motor_asyncio
from dotenv import load_dotenv
from base import  Poll, polling
from module import option as Option, vote
import cloudinary
import cloudinary.uploader
import cloudinary.api
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from dateutil import parser
load_dotenv()

cloudinary.config( 
  cloud_name = os.environ['CLOUD_NAME'], 
  api_key = os.environ['API_KEY'], 

  api_secret = os.environ['API_SECRET']
)



app = FastAPI()

origins = [
    "http://localhost:3000"

]
    

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.poll_backend
# async def browse_colletion():
#     await db['browser_collection'].create_index("date", expireAfterSeconds=7200)


@app.post("/poll/creation", response_description="user poll creation request", tags = ["poll"])
async def pollcreation( poll: Poll = Body(...)):
    try:
        polldetail = jsonable_encoder(poll) 
     
        # if  parser.parse(polldetail ['setenddate'])<=datetime.now() and polldetail ['setenddate']:
        #     return JSONResponse(status_code=404, content='please provide date after current date')

        if polldetail['imgtitle']:
            url  = cloudinary.uploader.upload(polldetail['imgtitle'])['url']
            polldetail['imgtitle'] = url  

        if polldetail['polltype']=="multipleOption":
            new_poll = await db["poll"].insert_one(polldetail)
            created_poll = await db['poll'].find_one({"_id": new_poll.inserted_id})  
            options  ={i:{'count':0} for i in polldetail['options']}
        else:
            polldetail['imageoptions'] = [{'text':val['text'], 'image':cloudinary.uploader.upload(val['image'])['url']}  for val in polldetail['imageoptions']]
            new_poll = await db["poll"].insert_one(polldetail)
            created_poll = await db['poll'].find_one({"_id": new_poll.inserted_id})  
            options = {val['text']:{'count':0, 'imageurl':val['image']}  for val in polldetail['imageoptions']}
       
        await db['results'].insert_one({'pollid': new_poll.inserted_id,'options':options })
        # print(await db['users'].find_one({'macaddr':polldetail['macaddr'] }))
        # if not await db['users'].find_one({'macaddr':polldetail['macaddr'] }):
           
        #     user_count  = db['users'].count()
        #     print(user_count)
    except Exception as e:
      
        return JSONResponse(status_code=400, content=e)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_poll)


@app.post("/poll/reply", response_description="user poll filling request", tags = ["poll"])
async def pollreply( poll: polling = Body(...)):
    try:
   
        polling = jsonable_encoder(poll)
        
        
        polldata = await db['poll'].find_one({"_id": polling['pollid']})
        if polldata['setenddate']:
            if datetime.now()>parser.parse(polldata['setenddate']) :
                return JSONResponse(status_code=400, content="you can't vote right now")


        pollid = polling['pollid']
        macaddr = polling['macaddr']
        choice = polling['choices']
        votingrestiction = polldata['votingrestiction']
        
        Voting = vote.Vote(db)

        if not await Voting.check(votingrestiction, pollid, macaddr):
            return JSONResponse(status_code=400, content="you can't vote right now")
        
        result  = await db['results'].find_one({'pollid':pollid})
        poll_options  =result['options']
        
        if not result:
            return JSONResponse(status_code=402, content="result for this pollid does not exist")
        
        result_val  = []
        total_votes  =  0
        
        
        for opt in choice:
            if type(opt) is dict:
                poll_options[opt['text']]['count'] = poll_options[opt['text']]['count'] +1

            else:
                poll_options[opt]['count'] = poll_options[opt]['count']+1
                
        for val in poll_options:
            total_votes+=poll_options[val]['count']
            if poll_options[val].get('imageurl')!=None:
                result_val.append({'text':val, 'count':poll_options[val]['count'], 'image':poll_options[val]['imageurl']})
            else:
                result_val.append({'text':val, 'count':poll_options[val]['count']})


        await db['results'].update_one({'pollid':pollid }, {"$set": {"options":poll_options}}, upsert=True)

    except Exception as e:
       
        return JSONResponse(status_code=400, content=e)
    

    
        
    
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"status":"vote accepted",'data':{'pollid':pollid,"totalcount":total_votes , "result_val":result_val}})

@app.post("/poll/detail/{pollid}", response_description="poll detail",tags = ["poll"])
async def poll_detail(pollid:str):
    
    return await db["poll"].find_one({"_id":pollid})



@app.post("/poll/result/{pollid}", response_description="poll results",tags = ["poll"])
async def poll_results(pollid:str):
    result  = await db["results"].find_one({"pollid":pollid})
    poll_options  =result['options']
    polltype =  await db["poll"].find_one({"_id":pollid})['polltype']
    if not result:
        return JSONResponse(status_code=402, content="result for this pollid does not exist")
    
    result_val  = []
    total_votes  =  0
       
    for val in poll_options:
        total_votes+=poll_options[val]['count']
        if poll_options[val].get('imageurl')!=None:
            result_val.append({'text':val, 'count':poll_options[val]['count'], 'image':poll_options[val]['imageurl']})
        else:
            result_val.append({'text':val, 'count':poll_options[val]['count']})

    return JSONResponse(status_code=200, content={'data':{"totalcount":total_votes , "result_val":result_val, "polltype":polltype}})



if __name__=="__main__":
    uvicorn.run("main:app",host='0.0.0.0', port=4557, reload=True, debug=True, workers=3)