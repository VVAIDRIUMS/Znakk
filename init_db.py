# init_db.py
import asyncio
import sys
import os

# Добавляем путь к проекту в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def init_database():
    """Инициализация базы данных"""
    try:
        from app.database.database import create_tables, engine
        
        print("🔄 Создание таблиц...")
        await create_tables()
        print("✅ Таблицы созданы!")
        
        # Проверка создания таблиц
        async with engine.begin() as conn:
            result = await conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = result.fetchall()
            print(f"📊 Создано таблиц: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")
        
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Проверьте структуру проекта и наличие всех файлов")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


async def create_sample_data():
    """Создание тестовых данных"""
    try:
        from app.database.database import AsyncSessionLocal
        from app.models.roles import RoleModel
        
        async with AsyncSessionLocal() as session:
            # Создаем базовые роли
            roles = ["admin", "user", "moderator"]
            for role_name in roles:
                role = RoleModel(name=role_name)
                session.add(role)
            
            await session.commit()
            print(f"✅ Созданы роли: {', '.join(roles)}")
            
    except Exception as e:
        print(f"⚠️ Не удалось создать тестовые данные: {e}")


async def main():
    """Основная функция"""
    print("=" * 50)
    print("🗄️ ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ")
    print("=" * 50)
    
    if await init_database():
        # Спросим о создании тестовых данных
        create_test = input("\nСоздать тестовые данные? (y/n): ").strip().lower()
        if create_test == 'y':
            await create_sample_data()
        
        print("\n" + "=" * 50)
        print("✅ База данных готова!")
        print("Файл: dating_app.db")
        print("=" * 50)
    else:
        print("\n❌ Не удалось инициализировать базу данных")


if __name__ == "__main__":
    # Для Windows может потребоваться специальная настройка event loop
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())