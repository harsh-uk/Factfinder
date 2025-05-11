from fastapi import FastAPI

from summarizer.routes import router

app = FastAPI()
app.include_router(router)
