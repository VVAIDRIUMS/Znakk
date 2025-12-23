# Исправление ошибки 422 (Unprocessable Entity)

## Проблема

При регистрации нового пользователя возникала ошибка **422 Unprocessable Entity**.

## Причина

Ошибка возникала из-за несоответствия данных между frontend и backend:

1. **Backend** (app/schemas/users.py): схема `SUserAdd` требовала обязательное поле `role_id`
2. **Frontend** (static/main.js): функция `registerUser()` отправляла только `email` и `password`
3. Отсутствовало обязательное поле `role_id` в JSON запросе регистрации

## Решение

Внесены изменения в 2 файла:

### 1. static/main.js (строка 110)

**Было:**
```javascript
body: JSON.stringify({ email, password })
```

**Стало:**
```javascript
body: JSON.stringify({ email, password, role_id: 1 })
```

### 2. app/schemas/users.py (строка 16)

**Было:**
```python
role_id: int = Field(..., ge=1, description="ID роли пользователя")
```

**Стало:**
```python
role_id: int = Field(1, ge=1, description="ID роли пользователя")
```

## Результат

✅ Регистрация пользователей теперь работает корректно
✅ Новым пользователям автоматически присваивается роль с `role_id = 1` (обычный пользователь)
✅ Frontend отправляет все необходимые поля для успешной валидации

## Дата исправления

23 декабря 2025 года

## Коммиты

- `Fix 422 error: add role_id to registerUser` - исправление frontend
- `Fix 422 error: make role_id optional with default value` - исправление backend
