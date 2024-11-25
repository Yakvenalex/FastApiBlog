from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.router import router as router_auth
from app.api.router import router as router_api
from app.pages.router import router as router_page
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Добавляем middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки
)

app.mount('/static', StaticFiles(directory='app/static'), name='static')


@app.get("/")
def home_page():
    return {
        "message": "Добро пожаловать! Пусть эта заготовка станет удобным инструментом для вашей работы и "
                   "приносит вам пользу!"
    }


app.include_router(router_auth)
app.include_router(router_api)
app.include_router(router_page)
