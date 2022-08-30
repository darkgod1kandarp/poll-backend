from typing import List

from numpy import False_


class MultipleOption:
    def __init__(self, options: List[str] , startnumber:int , endnumber:int  , number:int) -> None:
        self.dict1 = {i: 1 for i in options}
        self.startnumber  =  startnumber  
        self.endnumber =  endnumber
        self.number  =  number 

    def checking(self, useroptions: List[str]):
        count = 0
        for option in useroptions:
            if not self.dict1.get(option):
                count += 1
        
        if count > 1:
            return False
        
        if not self.dict1.get('other') and count > 0:
          
            return False

    def OptionChecking(self, useroptions: List[str], multipleoption: bool):

        # multipleoption = None if multipleoption=="None" else multipleoption
      
       
        if self.checking(useroptions) is False:
            return False
        
        if multipleoption == "None":
            if len(useroptions) > 1:
                return False

        elif multipleoption == "range":
            
            if not self.startnumber or not self.endnumber:
                return False
            if self.startnumber>self.endnumber:
                return False 
            if self.startnumber > len(useroptions) or self.endnumber < len(useroptions):
                return False

        elif multipleoption == "Exact number":
            
            if not self.number:
                return False
            if self.number != len(useroptions):
                return False

        return True

