from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class AppVariant(BaseModel):
    app_name: str
    variant_name: str
    parameters: Optional[Dict[str, Any]]
    previous_variant_name: Optional[str]


class Image(BaseModel):
    docker_id: str
    tags: str


class URI(BaseModel):
    uri: str
