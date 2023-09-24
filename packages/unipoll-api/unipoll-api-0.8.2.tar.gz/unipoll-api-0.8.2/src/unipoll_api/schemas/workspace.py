# from bson import DBRef
from pydantic import BaseModel, Field
from typing import Optional
from unipoll_api.documents import ResourceID


# Schema for the response with basic workspace info (name and role)
class Workspace(BaseModel):
    id: Optional[ResourceID]
    name: Optional[str]
    description: Optional[str]
    members: Optional[list]
    groups: Optional[list]
    policies: Optional[list]
    polls: Optional[list]

    class Config:
        schema_extra = {
            "example": {
                "id": "1a2b3c4d5e6f7g8h9i0j",
                "name": "Workspace 01",
                "description": "This is an example workspace",
            }
        }


class WorkspaceShort(BaseModel):
    id: ResourceID = Field(title="ID")
    name: str = Field(title="Name")
    description: str = Field(title="Description")


# Schema for the response with a list of workspaces
# It can be used to return a list of workspaces with basic info or full info
class WorkspaceList(BaseModel):
    workspaces: list[WorkspaceShort] | list[Workspace]

    class Config:
        schema_extra = {
            "example": {
                "workspaces": [
                    {
                        "name": "Workspace 01",
                        "description": "This is an example workspace",
                        "owner": "true",
                    },
                    {
                        "name": "Workspace 02",
                        "description": "This is another example workspace",
                        "owner": "false",
                    },
                ]
            }
        }


# Schema for the request to create a workspace
class WorkspaceCreateInput(BaseModel):
    name: str = Field(title="Name")
    description: str = Field(title="Description")

    class Config:
        schema_extra = {
            "example": {
                "name": "Workspace 01",
                "description": "This is an example workspace",
            }
        }


# Schema for the request to update a workspace
class WorkspaceUpdateRequest(BaseModel):
    name: Optional[str] = Field(title="Name")
    description: Optional[str] = Field(title="Description")

    class Config:
        schema_extra = {
            "example": {
                "name": "Workspace 01",
                "description": "This is an example workspace",
            }
        }


# Schema for the response when a workspace is created
class WorkspaceCreateOutput(BaseModel):
    id: ResourceID = Field(title="ID")
    name: str = Field(title="Name")
    description: str = Field(title="Description")

    class Config:
        schema_extra = {
            "example": {
                "name": "Workspace 01",
                "description": "This is an example workspace",
            }
        }
