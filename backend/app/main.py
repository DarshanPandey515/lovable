from fastapi import FastAPI
from app.routes.chat import router as chat_router


app = FastAPI(
    title="Mini Lovable",
    version="1.0"
)


app.include_router(chat_router)



@app.get("/")
def home():
    return {
        "message": "mini lovable clone"
    }
    