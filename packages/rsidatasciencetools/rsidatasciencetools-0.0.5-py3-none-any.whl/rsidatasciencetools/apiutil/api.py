import uvicorn
from fastapi import FastAPI, HTTPException
from typing import Optional
from enum import Enum
from pydantic import BaseModel
import os
from warnings import warn
import traceback
import json
from io import StringIO
import numpy as np
import pandas as pd
import pyodbc

# import the schemas for input and output objects (sample schema in this directory)
from python_schemas import Ping, ApiInput, ApiOutput


api = FastAPI()

@api.get('/api/ping', response_model=Ping)
async def get_map():
    ''' GET API function to test whether the API is
        functional.
    '''
    return {'isThere': True}

@api.post('/api/submit',response_model=ApiOutput)
async def submit(request: ApiInput):
    ''' Submit API function takes a json request and returns a json reponse
    '''
    data = json.loads(request.json())
    return {'Response' : "Hello there, " + data["Name"]}

@api.get('/api/get', response_model=ApiOutput)
async def get():
    return {'Response' : "Hello World"}

@api.get('/api/getSQL', response_model=ApiOutput)
async def get():
    con = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};' + 
        'SERVER=1242-LAP\PDB2019;DATABASE=FormsPOC2;' +
        f'UID={os.environ["RSI_SQL_USER"]};PWD={os.environ["RSI_SQL_PW"]}')
    cursor = con.cursor()
    cursor.execute("SELECT * FROM [dbo].[Form]") 
    row = cursor.fetchone()
    return {'Response' : "Hello"}            