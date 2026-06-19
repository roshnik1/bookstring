"""
# Server (main)
FastAPI Entry Point
"""

from pathlib import Path

from lxml.etree import _Element, _ElementTree

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from server.development import DocumentationSource, XMLResponse

from typing import (
    List,
)

server: FastAPI = FastAPI()
"""
FastAPI application instance
"""

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@server.get("/")
async def read_root():
    return {"Hello": "World"}

docs = DocumentationSource(dir=Path("../docs"))

@server.get("/dev/docs")
async def list_devdocs() -> List[str]:
    return docs.doclist

@server.get(
    "/dev/docs/{docname}",
    response_model=None,
    response_class=XMLResponse
)
async def devdoc(docname: str):
    doc = docs.get_document(docname)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find dev document '{docname}'"
        )
    return XMLResponse(content=doc)