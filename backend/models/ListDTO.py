from dataclasses import dataclass
from typing import Any, List

@dataclass
class ListDTO:
    def __init__(self, page: int, pageSize: int, list: List[Any]):
        self.page = page
        self.pageSize = pageSize
        self.totalResults = len(list)
        self.Items = list
