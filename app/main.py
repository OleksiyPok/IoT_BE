# app/main.py

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

load_dotenv()
from app.router import router

app = FastAPI(
    title="IoT Backend (Oleksii Pokormiakho)",
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


STATIC_DIR = Path(__file__).parent / "static"


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(STATIC_DIR / "led_control.html")


app.include_router(router)
