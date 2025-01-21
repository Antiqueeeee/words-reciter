from pydantic import BaseModel
from typing import List, Optional

class params_publisher_select_word(BaseModel):
    publisher: str  # 出版社
    grade: str  # 年级
    edition: str  # 版次
    volume: str  # 上下册
    unit : Optional[str] = None