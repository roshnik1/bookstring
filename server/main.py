from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

server = FastAPI()

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@server.get("/")
def read_root():
    return {"Hello": "World"}