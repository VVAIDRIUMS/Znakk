import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.auth import router as auth_router
from app.api.roles import router as roles_router
from app.router.favorites import router as favorites_router
from app.router.likes import router as likes_router
from app.router.profiles import router as profiles_router
from app.router.user_filters import router as user_filters_router
from app.router.users import router as users_router
from app.database.database import create_tables

app = FastAPI(title="Сайт Знакомств", version="0.0.1")

app.include_router(auth_router)
app.include_router(roles_router)
app.include_router(favorites_router)
app.include_router(likes_router)
app.include_router(profiles_router)
app.include_router(users_router)
app.include_router(user_filters_router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint - serve the frontend
@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

# API endpoint to get profiles (demo)
@app.get("/api/profiles")
async def get_profiles():
    # Return sample profiles for demo
    return [
        {"id": 1, "name": "Анна", "age": 24, "city": "Москва", "bio": "Люблю кофе и путешествия", "photo": "https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg?w=800&q=80"},
        {"id": 2, "name": "Данил", "age": 27, "city": "Санкт-Петербург", "bio": "Музыка, спорт, кино", "photo": "https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg?w=800&q=80"},
        {"id": 3, "name": "Катя", "age": 22, "city": "Москва", "bio": "Фотограф и художник", "photo": "https://images.pexels.com/photos/1181686/pexels-photo-1181686.jpeg?w=800&q=80"},
        {"id": 4, "name": "Илья", "age": 29, "city": "Екатеринбург", "bio": "IT-специалист, люблю программировать", "photo": "https://images.pexels.com/photos/2379004/pexels-photo-2379004.jpeg?w=800&q=80"},
        {"id": 5, "name": "Маша", "age": 26, "city": "Казань", "bio": "Кондитер, пеку торты", "photo": "https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?w=800&q=80"},
        {"id": 6, "name": "Олег", "age": 31, "city": "Новосибирск", "bio": "Инженер, увлекаюсь техникой", "photo": "https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?w=800&q=80"},
        {"id": 7, "name": "Света", "age": 23, "city": "Владивосток", "bio": "Художница, рисую портреты", "photo": "https://images.pexels.com/photos/3777916/pexels-photo-3777916.jpeg?w=800&q=80"},
        {"id": 8, "name": "Никита", "age": 28, "city": "Ростов-на-Дону", "bio": "Разработчик, люблю Python", "photo": "https://images.pexels.com/photos/2379004/pexels-photo-2379004.jpeg?w=800&q=80"},
        {"id": 9, "name": "Лера", "age": 25, "city": "Красноярск", "bio": "Музыкант, играю на гитаре", "photo": "https://images.pexels.com/photos/1239291/pexels-photo-1239291.jpeg?w=800&q=80"},
        {"id": 10, "name": "Павел", "age": 30, "city": "Воронеж", "bio": "Путешественник, люблю природу", "photo": "https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg?w=800&q=80"},
        {"id": 11, "name": "Оля", "age": 27, "city": "Самара", "bio": "Дизайнер, работаю с брендами", "photo": "https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg?w=800&q=80"},
        {"id": 12, "name": "Роман", "age": 33, "city": "Омск", "bio": "Фотограф, снимаю ночью", "photo": "https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?w=800&q=80"},
        {"id": 13, "name": "Юля", "age": 24, "city": "Уфа", "bio": "Йога и медитация", "photo": "https://images.pexels.com/photos/1181686/pexels-photo-1181686.jpeg?w=800&q=80"},
        {"id": 14, "name": "Артем", "age": 26, "city": "Челябинск", "bio": "Спортсмен, тренер по фитнесу", "photo": "https://images.pexels.com/photos/2379004/pexels-photo-2379004.jpeg?w=800&q=80"},
        {"id": 15, "name": "Вика", "age": 28, "city": "Пермь", "bio": "Блогер, пишу о путешествиях", "photo": "https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?w=800&q=80"}
    ]

@app.on_event("startup")
async def startup_event():
    await create_tables()
    print("✅ База данных инициализирована")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)