import os
from fastapi import FastAPI, Body, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import motor.motor_asyncio
from dotenv import load_dotenv
from base import User, UserLogin, Poll, polling
from module import option as Option, vote


load_dotenv()

cloudinary.uploader.upload("/home/om/Pictures/Screenshot from 2022-08-17 22-32-19.png")

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.poll_backend
db['browser_collection'].create_index("date", expireAfterSeconds=7200)


@app.post("/signup", response_description="signup of the user",  response_model=User)
async def signup(user: User = Body(...)):

    user = jsonable_encoder(user)
    new_user = await db["users"].insert_one(user)
    created_student = await db["users"].find_one({"_id": new_user.inserted_id})

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_student)


@app.post("/signin", response_description="signin of the user")
async def signin(user: UserLogin = Body(...)):
    user = jsonable_encoder(user)
    find_user = await db["users"].find_one({"name": "Jane Doe"})
    if find_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Student {id} not found")
    return JSONResponse(status_code=status.HTTP_201_CREATED)


@app.post("/poll/creation", response_description="user poll creation request")
async def pollcreation(request: Request, poll: Poll = Body(...)):
    polldetail = jsonable_encoder(poll)
    new_poll = await db["poll"].insert_one(polldetail)
    created_poll = await db['poll'].find_one({"_id": new_poll.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_poll)


@app.post("/poll/reply", response_description="user poll filling request")
async def pollreply(request: Request, poll: polling = Body(...)):

    polling = jsonable_encoder(poll)
    polldata = await db['poll'].find_one({"_id": polling['pollid']})

    pollid = polling['pollid']
    macaddr = polling['macaddr']
    userid = polling['userid']
    choice = polling['choices']

    option = polldata['options']
    case = polldata['multipleoption']
    votingrestiction = polldata['votingrestiction']

    val = [i for i in case.keys()][0]

    multopt = Option.MultipleOption(option)

    if multopt.OptionChecking(choice, val, case[val]) is False:
        return JSONResponse(status_code=400, content="number of option is not correct")

    Voting = vote.Vote(db)

    if not await Voting.check(votingrestiction, userid, request, pollid, macaddr):
        return JSONResponse(status_code=400, content="you can't vote right now")
    
    
    return JSONResponse(status_code=status.HTTP_201_CREATED, content="vote accepted")
