from dataclasses import dataclass, field
from typing import ClassVar, Any, Dict, List


@dataclass
class DbTable:
    
    name: str=""
    columns: list = field(default_factory=list) #[{"name":"","type":"","db_key":""}]
    is_rolled: bool=False
    project_uid: int=0
    
    uid: str = field(init=False)
    instance_counter: ClassVar[int] = 0


    def __post_init__(self):
        self.__class__.instance_counter += 1
        self.uid = str(self.instance_counter)
        
