from dataclasses import dataclass
from typing import Optional, List


@dataclass
class AttributeInput:
    attribute_name: str
    description: str
    required: Optional[bool] = None
    attr_type: Optional[str] = None
    version_added: Optional[str] = None
    version_removed: Optional[str] = None
    doc_anchor: Optional[str] = None


@dataclass
class ResourceInput:
    provider: str
    resource_name: str
    version: str
    doc_url: str
    attributes: List[AttributeInput]
