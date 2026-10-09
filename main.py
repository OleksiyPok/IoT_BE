# BE/main.py

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
from router import router

app = FastAPI(
    title="IoT Backend",
    swagger_ui_parameters={
        "docExpansion": "none",
    },
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # демо; у проді — список
    allow_credentials=False,  # no cookies
    allow_methods=["GET", "POST"],  # default — only GET
    allow_headers=["Content-Type"],
)

app.include_router(router)
