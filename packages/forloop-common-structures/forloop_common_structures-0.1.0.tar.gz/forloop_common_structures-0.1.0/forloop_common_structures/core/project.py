from dataclasses import dataclass, field
from typing import ClassVar, Any, Dict, List, Optional


@dataclass
class Project:
    
    project_name: str=""
    project_key: str="" #will be used as URL extension e.g. app.forloop.ai/jh45FsR45xyE
    last_active_pipeline_uid: Optional[str]=None    
    uid: str = field(init=False)
    instance_counter: ClassVar[int] = 0


    def __post_init__(self):
        self.__class__.instance_counter += 1
        self.uid = str(self.instance_counter)
        
