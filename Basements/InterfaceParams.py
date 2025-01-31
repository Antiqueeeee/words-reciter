from pydantic import BaseModel
from typing import List, Optional

class params_publisher_select_word(BaseModel):
    publisher: str  # 出版社
    grade: str  # 年级
    edition: str  # 版次
    volume: str  # 上下册
    unit : Optional[str] = None

class params_get_grades(BaseModel):
    publisher: str

class params_get_volumes(BaseModel):
    publisher: str
    grade: str

class params_get_editions(BaseModel):
    publisher: str
    grade: str
    volume: str

class params_get_units(BaseModel):
    publisher: str
    grade: str
    volume: str
    edition: str

class params_get_word_audio(BaseModel):
    filename: str

class params_obtain_word_related(BaseModel):
    word : str