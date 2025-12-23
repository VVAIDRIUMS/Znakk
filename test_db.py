# test_db.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String

# Создаем движок для SQLite
DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()

# Простая модель
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

async def main():
    print("Тестирование SQLAlchemy с SQLite...")
    
    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Таблицы созданы!")
    
    # Создаем сессию
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Добавляем тестового пользователя
        user = User(name="Тестовый пользователь")
        session.add(user)
        await session.commit()
        print(f"✅ Добавлен пользователь: {user.name}")
    
    print("🎉 SQLAlchemy работает корректно!")

if __name__ == "__main__":
    asyncio.run(main())