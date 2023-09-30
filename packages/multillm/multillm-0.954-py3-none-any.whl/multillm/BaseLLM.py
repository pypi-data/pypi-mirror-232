# ==============================================================================
# Copyright 2023 VerifAI All Rights Reserved.
# https://www.verifai.ai
# License: 
#
# ==============================================================================


import os
import sys

from typing import List, Dict

sys.path.append(os.path.join(os.path.dirname(__file__), "."))
from Prompt import *
from Redis import *

"""
The BaseModel class declares several attributes such as model, roles, messages, temp, api_key, max_tokens, and args.
It also defines two methods: __init__() and get_response().
The __init__() method is empty and does not perform any action. 
The get_response() method is a placeholder that needs to be implemented by the user.
"""
class BaseLLM(object):

    model: str

    roles: List[str]

    messages: List[List[str]]

    temp: float

    api_key: str

    max_tokens: int

    args: str

    def __init__(self, **kwargs):

        # if values are specified in **kwargs, over-ride defaults 
        try:
            self.name = kwargs['name']
        except:
            pass

        # set credentials json file
        try:
            self.credentials = kwargs['credentials']
        except:
            pass

        # set default model name
        try:
            self.model = kwargs['model']
        except:
            pass

        # set class name
        try:
            self.class_name = kwargs['class_name']
        except:
            pass

       

    def get_response(self, Prompt):
        # Pass in Prompt object and run model with prompt
        return

    def get_content(self, response):
        # Implementer needs to write interface for this
        return


    def is_code(self, response):
        import re
        regex_pattern = r"```(?:[a-zA-Z]+)?(?:[a-zA-Z]+\n)?([^`]+)(?:```)?"
        matches = re.findall(regex_pattern, response)
        if matches:
            return True
        else:
            return False
    

    def publish_to_redis(self, response, taskid):

        
        #publish to redis
        if taskid:
            meta_data = {"type": "response", "model_name": self.__class__.__name__}
            Redis.publish_to_redis(type="multillm", 
                                    taskid=taskid, 
                                    result=response, 
                                        meta_data=meta_data)
    

    
