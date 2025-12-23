# 🧪 Основное руководство по тестированию

## ✅ Последние исправления

1. Обновлен класс `InvalidCredentialsException` - теперь принимает опциональное сообщение
2. Исправлены все вызовы исключений в сервисе аутентификации
3. Улучшена обработка ошибок в API

---

## 1. Установка и запуск

### Прередысловки:

```bash
# Обновить зависимости
pip install -r requirements.txt

# Или если используете uv
uv sync
```

### Запуск сервера:

```bash
uvicorn main:app --reload --port 8001
```

Вы должны увидеть такое сообщение:

```
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Application startup complete
✅ База данных инициализирована
```

---

## 2. ТЕСТИРОВАНИЕ НА Всех UNIX (используйте `curl`)

### 2.1. ПРОВЕРКА ПО ЗдОровью

```bash
curl -X GET http://localhost:8001/auth/health
```

**Ожидаемый ответ:**
```json
{"status": "healthy"}
```

---

### 2.2. РЕГИСТРАЦИЯ - НОВОМУ ПОЛьзователю

```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123",
    "role_id": 1
  }'
```

**Ожидаемый ответ (201 Created):**
```json
{
  "email": "test@example.com",
  "is_active": true,
  "id": 1,
  "role_id": 1,
  "created_at": "2025-12-23T15:05:00.000000"
}
```

✅ **Отлично! Регистрация работает!**

---

### 2.3. ПОПЫТКА РЕГИСТРАЦИИ - ВТОРОГО МЕВО u0430 Новом аккунтом

```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123",
    "role_id": 1
  }'
```

**Ожидаемый ответ (409 Conflict):**
```json
{
  "detail": "User with email 'test@example.com' already exists"
}
```

✅ **Отлично! Проверка дубликатов работает!**

---

### 2.4. ВХОД - ЧЕРЕЗ JSON (РОМЕНДУЕТСЯ)

```bash
curl -X POST http://localhost:8001/auth/login-json \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

**Ожидаемый ответ (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "role_id": 1
}
```

✅ **Отлично! Вход работает!**

Сохраните `access_token` - он вам понаробится для авторизации!

---

### 2.5. ВХОД - НЕВЕРНОЕ ПАРОЛЬ

```bash
curl -X POST http://localhost:8001/auth/login-json \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "WrongPassword"
  }'
```

**Ожидаемый ответ (401 Unauthorized):**
```json
{
  "detail": "Invalid password"
}
```

✅ **Отлично! Проверка пароля работает!**

---

### 2.6. ВХОД - НЕСУЩЕСТВУЮЩИЙ ПОЛьЗОВАТЕЛЬ

```bash
curl -X POST http://localhost:8001/auth/login-json \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nonexistent@example.com",
    "password": "SecurePass123"
  }'
```

**Ожидаемый ответ (401 Unauthorized):**
```json
{
  "detail": "User not found"
}
```

✅ **Отлично! Проверка наличия пользователя работает!**

---

## 3. ОШИБКИ КОТОРЫЕ МЫ ИСПРАВИЛИ

### Проблема #1: `InvalidCredentialsException` не принимал аргументы

**Было:**
```python
class InvalidCredentialsException(Exception):
    def __init__(self):
        super().__init__("Incorrect email or password")
```

**Теперь:**
```python
class InvalidCredentialsException(Exception):
    def __init__(self, message: str = "Incorrect email or password"):
        super().__init__(message)
        self.message = message
```

---

### Проблема #2: Непонятные вызовы исключений

**Было:**
```python
if not user:
    raise InvalidCredentialsException()  # Нет сообщения!
```

**Теперь:**
```python
if not user:
    raise InvalidCredentialsException("User not found")  # Есть сообщение!
```

---

### Проблема #3: API не обрабатывал исключения

**Было:**
```python
except InvalidCredentialsException:  # Отловлена без вариантов!
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный email или пароль",  # Генеричные сообщения
        headers={"WWW-Authenticate": "Bearer"}
    )
```

**Теперь:**
```python
except InvalidCredentialsException as e:  # Передаем аргумент
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=str(e),  # Уникальные сообщения!
        headers={"WWW-Authenticate": "Bearer"}
    )
```

---

## 4. ТЕМПЛЕТЫ curl для выкопирования

### Быстрая понедельника тестирования

```bash
#!/bin/bash

# Нумер 1: Health check
echo "=== Health Check ==="
curl http://localhost:8001/auth/health | jq

# Нумер 2: Регистрация
echo -e "\n=== Registration ==="
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user'$(date +%s)'@example.com",
    "password": "SecurePass123",
    "role_id": 1
  }' | jq

# Нумер 3: Вход
echo -e "\n=== Login ==="
curl -X POST http://localhost:8001/auth/login-json \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }' | jq

# Нумер 4: Неверный пароль
echo -e "\n=== Invalid Password ==="
curl -X POST http://localhost:8001/auth/login-json \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "WrongPassword"
  }' | jq
```

---

## 5. КШО ПОЛУЧИЛ СООбЩение

| Исключение | HTTP Code | Ответ | Причина |
|-----------|-----------|--------|----------|
| `UserAlreadyExistsException` | 409 | User already exists | Однако email еже регистрацию |
| `InvalidCredentialsException` | 401 | Invalid email/password | Неверные данные |
| `UserNotFoundException` | 404 | User not found | Пользователь не найден |
| `InvalidPasswordException` | 400 | Password error | Пароль не подходит |

---

## 6. Что следует сделать дальше

⚠️ **ВАЖНО** для Production:

1. Не жесткокодировать SECRET_KEY в коде:
   ```python
   import os
   SECRET_KEY = os.getenv("SECRET_KEY", "default-insecure-key")
   ```

2. Проверить сроки валидации токенов:
   ```python
   ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Разумное значение
   ```

3. Декодировать JWT в реальных Depends:
   ```python
   async def get_current_user(token: str = Depends(oauth2_scheme)):
       # Валидировать токен
       pass
   ```

4. Отключить отладку (remove `print()` statements)

5. Понастроить логирование

---

✅ **Всё готово к тестированию!**
