from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import ClassVar, Optional, Union

from forloop_common_structures.core.edge import Edge
from src.core.node import Node
from forloop_common_structures.core.variable import Variable


class JobSortableColumnsEnum(str, Enum):
    STATUS = "status"
    CREATED_AT = "created_at"
    COMPLETED_AT = "completed_at"
    PIPELINE_UID = "pipeline_uid"


class JobTypeEnum(str, Enum):
    PIPELINE = "PIPELINE"
    NODE = "NODE"


class JobStatusEnum(str, Enum):
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"


@dataclass
class BaseJob:
    uid: Optional[str] = None
    machine_uid: Optional[str] = None
    status: JobStatusEnum = JobStatusEnum.QUEUED
    created_at: float = field(
        default_factory=lambda: datetime.utcnow().timestamp()
    )  # UNIX timestamp
    started_at: Optional[float] = None  # UNIX timestamp
    completed_at: Optional[float] = None  # UNIX timestamp
    message: Optional[str] = None

    instance_counter: ClassVar[int] = 0

    def __post_init__(self) -> None:
        # Deserialize into Enum if instantiated from JSON
        if isinstance(self.status, str):
            self.status = JobStatusEnum(self.status)


@dataclass
class NodeJob(BaseJob):
    node_uid: str = ""  # HACK: must have a default value, otherwise it's a non-default arg which proceeds default args from BaseJob
    node: Optional[Node] = None
    type: JobTypeEnum = JobTypeEnum.NODE

    def __post_init__(self):
        super().__post_init__()
        # Deserialize dict into a Node if NodeJob is instantiated from a JSON
        if isinstance(self.node, dict):
            uid = self.node.pop("uid")
            # Node initializes it's own uid, so we replace it with the original uid
            self.node = Node(**self.node)
            self.node.uid = uid

        # Deserialize into Enum if instantiated from JSON
        if isinstance(self.type, str):
            self.type = JobTypeEnum(self.type)


# Dataclass 'type' attribute is shadowing built-in 'type', hence type hint is shifted outside of PipelineJob
DeserializableObjects = Union[type[Node], type[Edge], type[Variable]]


@dataclass
class PipelineJob(BaseJob):
    pipeline_uid: str = ""  # HACK: must have a default value, otherwise it's a non-default arg which proceeds default args from BaseJob
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    variables: list[Variable] = field(default_factory=list)
    jobs: list[NodeJob] = field(default_factory=list)
    type: JobTypeEnum = JobTypeEnum.PIPELINE

    def __post_init__(self) -> None:
        super().__post_init__()

        # Deserialize into Enum if instantiated from JSON
        if isinstance(self.type, str):
            self.type = JobTypeEnum(self.type)

        # Deserialize list[dict] into a list[NodeJob] if PipelineJob is instantiated from a JSON
        if self.jobs and isinstance(self.jobs[0], dict):
            self.jobs = [NodeJob(**job) for job in self.jobs]

        for obj in [Node, Edge, Variable]:
            self._deserialize_object(obj)

    def _deserialize_object(self, obj: DeserializableObjects) -> None:
        """Deserialize nodes, edges, variables into list of objects in case the Job was instantiated from JSON."""
        name_mapping = {Node: "nodes", Edge: "edges", Variable: "variables"}

        attr_name = name_mapping[obj]
        list_of_dicts: list = getattr(self, attr_name)

        # Deserialize into corresponding object if instantiated from dict (json)
        if list_of_dicts and isinstance(list_of_dicts[0], dict):
            objects = []
            for dic in list_of_dicts:
                uid = dic.pop("uid")
                # Object initializes uid during instantiation, so we replace it with the original uid
                dic = obj(**dic)
                dic.uid = uid
                objects.append(dic)
            setattr(self, attr_name, objects)
