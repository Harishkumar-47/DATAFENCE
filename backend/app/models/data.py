from pydantic import BaseModel
from typing import List


class PersonalData(BaseModel):
    category: str
    value: str
    sensitivity: str
    source: str


class DataSource(BaseModel):
    name: str
    type: str
    data_collected: List[str]
    risk_level: str