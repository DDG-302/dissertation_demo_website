from fastapi import Body, Form
from pydantic import BaseModel
from dataclasses import dataclass

# @dataclass
class QueryRequest(BaseModel):
    query:str