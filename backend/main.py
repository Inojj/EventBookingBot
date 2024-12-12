import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status
from const.user import USER, PASS

from app.database import init_db
from app.routes import events, bookings

# Создание приложения FastAPI
from utils.oauth import create_access_token

app = FastAPI(
    title="Event Booking API",
    description="API для управления мероприятиями и бронированиями",
    version="1.0.0",
)

fake_users_db = {
    USER: {"username": USER, "password": PASS}
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Настройка CORS (если требуется)
origins = [
    "http://localhost:3000",  # Разрешённые источники (например, React-приложение)
    "http://127.0.0.1:3000",
    "http://localhost:9000",
    "http://46.226.161.114:3000",
    "http://46.226.161.114:8500",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Укажите список разрешённых источников
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

public_routes = ["/token", "/docs", "/openapi.json"]


# Событие при запуске приложения
@app.on_event("startup")
async def startup_event():
    await init_db()  # Инициализация базы данных


# Подключение маршрутов
app.include_router(events.router)
app.include_router(bookings.router)


# Проверочный маршрут
@app.get("/", tags=["Health Check"])
async def health_check():
    return {"status": "ok"}


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учетные данные")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=9000, reload=True)
