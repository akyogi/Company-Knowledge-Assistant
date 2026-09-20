from fastapi import FastAPI
from routers import home

##This is the main file

app =FastAPI()
app.include_router(home.router)


