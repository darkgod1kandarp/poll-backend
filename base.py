
from pydantic import BaseModel, Field, EmailStr, validator
from bson import ObjectId
from typing import Dict, List, Union
from typing import List, Optional
from datetime import date, datetime
from enum import Enum


class VotingRestriction(str, Enum):
    zero = "unlimited votes per user"
    one = "One vote browser session"
    two = "One vote per IP address"


class ResultsVisibility(str, Enum):
    zero = "Always public"
    one = "Public after end date"
    two = "Public after vote"
    three = "Not public"


class MultipleOption(str, Enum):
    zero = "Exact number"
    one = "unlimited"
    two = "range"
    three = "None"
class PollOption(str, Enum):
    one  =  "multipleOption"
    two  =  "imagePoll"


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class polling(BaseModel):
    macaddr: str = Field(...)
    pollid: str = Field(...)
    choices: List

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "macaddr": "wqwf",
                "pollid": "630ca07331ad946501f83f9d",
                "choices": ["not yet", "yes doing fine work"]
            }
        }


class Poll(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str = Field(...)
    imgtitle: Optional[str] = None
    description: Optional[str] =None
    options: Optional[List[str]] = None
    multipleoption: Dict[str, MultipleOption]
    imageoptions: Optional[List[Dict[str, str]]] = None
    setenddate: Union[ bool, datetime]
    allowcomments: bool
    votingrestiction: VotingRestriction
    startnumber: Optional[int] = None
    number: Optional[int] = None
    endnumber: Optional[int] = None
    polltype:PollOption

    @validator("setenddate", pre=True)
    def parse_setenddate(cls, value):
       
        if value :
            generator_date = (i for i in map(int, value.split("/")))
      
        
            return datetime(next(generator_date), next(generator_date), next(generator_date), next(generator_date), next(generator_date), next(generator_date))
        else:
            return False

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "title": "BJP doing fine work ?",
                "description": "Bjp survey",
                "options": ["not yet", "yes doing fine work"],
                "multipleoption": {"type": "range"},
                "setenddate": "2024/5/8/6/55/0",
                "votingrestiction": "One vote browser session",
                "allowcomments": False,
                "startnumber": 1,
                "endnumber": 3,
                "polltype":"multipleOption"

            }
        }



# class Comment(BaseModel):
#     pollid:str 
    


# {
#   "title": "BJP doing fine work ?",
#   "description": "Bjp survey",
#   "imageoptions": [
    
#       {
#         "text":"not yet"
    
#     ,"image":"data:image/png;base64|,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
        
#       },
    
#     {"text":"yes doing fine work", 
#     "image":"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="}
#   ],
#   "multipleoption": {
#     "type": "range"
#   },
#   "setenddate": "2024/5/8/6/55/0",
#   "votingrestiction": "One vote browser session",
#   "allowcomments": false,
#   "startnumber": 1,
#   "endnumber": 2,
#   "pollType":"imagePoll"
# }