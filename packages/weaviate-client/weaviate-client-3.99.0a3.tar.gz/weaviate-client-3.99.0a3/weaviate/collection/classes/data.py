import uuid as uuid_package
from dataclasses import dataclass
from typing import List, Optional, Dict, Union, Generic

from weaviate.collection.classes.internal import Properties
from weaviate.util import _to_beacons
from weaviate.types import UUID, UUIDS


@dataclass
class Error:
    message: str
    code: Optional[int] = None
    original_uuid: Optional[UUID] = None


@dataclass
class _BatchReturn:
    """This class contains the results of a batch `insert_many` operation.

    Since the individual objects within the batch can error for differing reasons, the data is split up within this class for ease use when performing error checking, handling, and data revalidation.

    Attributes:
        all_responses: A list of all the responses from the batch operation. Each response is either a `uuid_package.UUID` object or an `Error` object.
        uuids: A dictionary of all the successful responses from the batch operation. The keys are the indices of the objects in the batch, and the values are the `uuid_package.UUID` objects.
        errors: A dictionary of all the failed responses from the batch operation. The keys are the indices of the objects in the batch, and the values are the `Error` objects.
        has_errors: A boolean indicating whether or not any of the objects in the batch failed to be inserted. If this is `True`, then the `errors` dictionary will contain at least one entry.
    """

    all_responses: List[Union[uuid_package.UUID, Error]]
    uuids: Dict[int, uuid_package.UUID]
    errors: Dict[int, Error]
    has_errors: bool = False


@dataclass
class RefError:
    message: str


@dataclass
class ReferenceTo:
    uuids: UUIDS

    @property
    def uuids_str(self) -> List[str]:
        if isinstance(self.uuids, list):
            return [str(uid) for uid in self.uuids]
        else:
            return [str(self.uuids)]

    def to_beacons(self) -> List[Dict[str, str]]:
        return _to_beacons(self.uuids)


@dataclass
class ReferenceToMultiTarget(ReferenceTo):
    target_collection: str

    def to_beacons(self) -> List[Dict[str, str]]:
        return _to_beacons(self.uuids, self.target_collection)


@dataclass
class BatchReference:
    from_uuid: UUID
    to_uuid: UUID


@dataclass
class DataObject(Generic[Properties]):
    properties: Properties
    uuid: Optional[UUID] = None
    vector: Optional[List[float]] = None
