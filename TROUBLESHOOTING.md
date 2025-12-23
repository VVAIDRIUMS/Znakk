# Устранение неполадок при запуске приложения

## Ошибка: ModuleNotFoundError: No module named 'app.api.auth'

### Проблема

```
File "c:\Users\Vadimka\Documents\Znak\Znak\Znak\main.py", line 5, in <module>
    from app.api.auth import router as auth_router
ModuleNotFoundError: No module named 'app.api.auth'
```

### Причины

1. **Неправильная структура каталогов** - путь `Znak\Znak\Znak\main.py` указывает на тройную вложенность
2. **Запуск из неправильной директории**
3. **Не установлен пакет в режиме разработки**

### Решение

#### Шаг 1: Проверьте структуру проекта

Правильная структура должна быть:

```
Znakk/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── roles.py
│   ├── router/
│   │   ├── __init__.py
│   │   ├── favorites.py
│   │   ├── likes.py
│   │   ├── profiles.py
│   │   ├── user_filters.py
│   │   └── users.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── database/
├── static/
│   ├── index.html
│   ├── style.css
│   └── main.js
├── main.py
├── requirements.txt
└── README.md
```

**НЕ должно быть:**
```
Znak/
└── Znak/
    └── Znak/  ❌ Тройная вложенность!
        └── main.py
```

#### Шаг 2: Переместите файлы в правильную директорию

1. Откройте проводник Windows
2. Перейдите в `c:\Users\Vadimka\Documents\`
3. Найдите папку с проектом
4. Убедитесь, что `main.py` находится на том же уровне, что и папка `app/`

#### Шаг 3: Откройте терминал в КОРНЕВОЙ директории проекта

Откройте командную строку (cmd) или PowerShell:

```bash
cd c:\Users\Vadimka\Documents\Znakk
```

Или в проводнике: правая кнопка мыши → "Открыть в терминале"

#### Шаг 4: Проверьте наличие всех __init__.py файлов

Убедитесь, что существуют следующие файлы (даже если пустые):

```
app/__init__.py
app/api/__init__.py
app/router/__init__.py
app/models/__init__.py
app/schemas/__init__.py
app/services/__init__.py
app/database/__init__.py
```

#### Шаг 5: Установите зависимости

```bash
pip install -r requirements.txt
```

#### Шаг 6: Запустите приложение

```bash
python main.py
```

ИЛИ с uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Альтернативное решение: Использование PYTHONPATH

Если структура проекта правильная, но ошибка сохраняется:

**Windows (CMD):**
```bash
set PYTHONPATH=%cd%
python main.py
```

**Windows (PowerShell):**
```powershell
$env:PYTHONPATH = (Get-Location).Path
python main.py
```

**Linux/Mac:**
```bash
export PYTHONPATH=$(pwd)
python main.py
```

### Проверка правильности установки

Выполните следующие команды для проверки:

```bash
# Проверка текущей директории
pwd  # Linux/Mac
cd   # Windows

# Проверка структуры
dir app  # Windows
ls app   # Linux/Mac

# Проверка Python пути
python -c "import sys; print('\n'.join(sys.path))"
```

### Ожидаемый результат

При успешном запуске вы должны увидеть:

```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
✅ База данных инициализирована
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Дополнительные проверки

#### Проверка импорта вручную

Откройте Python в терминале и попробуйте импортировать модули:

```bash
python
>>> from app.api.auth import router
>>> print(router)
>>> exit()
```

Если импорт работает - проблема в запуске, если нет - проблема в структуре.

### Если ничего не помогло

1. **Удалите кэш Python:**
   ```bash
   # Windows
   del /s /q __pycache__
   del /s /q *.pyc
   
   # Linux/Mac
   find . -type d -name "__pycache__" -exec rm -r {} +
   find . -type f -name "*.pyc" -delete
   ```

2. **Пересоздайте виртуальное окружение:**
   ```bash
   # Удалите старое
   rmdir /s venv  # Windows
   rm -rf venv    # Linux/Mac
   
   # Создайте новое
   python -m venv venv
   
   # Активируйте
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   
   # Установите зависимости
   pip install -r requirements.txt
   ```

3. **Проверьте версию Python:**
   ```bash
   python --version
   ```
   Должна быть Python 3.8 или выше.

## Другие частые ошибки

### Ошибка: Port already in use

```bash
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8001 | xargs kill -9
```

### Ошибка: Database connection failed

Убедитесь, что файл базы данных создан:
```bash
python init_db.py
```

## Контакты для поддержки

Если проблема не решена, создайте Issue на GitHub с:
- Полным текстом ошибки
- Выводом команды `python --version`
- Структурой директорий (`tree` или `dir /s`)
- Операционной системой
