# API Integration Documentation

## Обзор

Фронтенд приложения теперь разделен на отдельные файлы и полностью интегрирован с бэкенд API.

## Структура файлов

```
static/
├── index.html    # Чистая HTML структура без встроенных стилей/скриптов
├── style.css     # Все CSS стили (включая темную тему и адаптивный дизайн)
└── main.js       # JavaScript логика с API интеграцией
```

## API Endpoints

### Аутентификация

#### POST `/auth/register`
**Описание:** Регистрация нового пользователя

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2025-12-23T14:42:00"
}
```

#### POST `/auth/login`
**Описание:** Вход пользователя

**Request Body (form-urlencoded):**
```
username=user@example.com&password=password123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Профили

#### GET `/profiles/`
**Описание:** Получить список профилей с фильтрацией

**Query Parameters:**
- `city` (optional): Фильтр по городу
- `gender` (optional): Фильтр по полу (male/female)
- `skip` (optional): Количество пропущенных записей
- `limit` (optional): Максимальное количество записей

**Response:**
```json
[
  {
    "id": 1,
    "name": "Анна",
    "age": 24,
    "gender": "female",
    "city": "Москва",
    "bio": "Люблю кофе и путешествия",
    "photo_url": "https://example.com/photo.jpg",
    "contact_info": "@anna_travel",
    "tags": ["путешествия", "кофе", "фотография"],
    "user_id": 1
  }
]
```

#### POST `/profiles/`
**Описание:** Создать новый профиль

**Request Body:**
```json
{
  "name": "Анна",
  "age": 24,
  "gender": "female",
  "city": "Москва",
  "bio": "Люблю кофе и путешествия",
  "photo_url": "https://example.com/photo.jpg",
  "contact_info": "@anna_travel",
  "tags": ["путешествия", "кофе"]
}
```

**Headers:**
```
Authorization: Bearer <token>
```

#### PUT `/profiles/{profile_id}`
**Описание:** Обновить существующий профиль

**Request Body:** Аналогичен POST `/profiles/`

### Лайки

#### POST `/likes/`
**Описание:** Лайкнуть профиль

**Request Body:**
```json
{
  "liked_profile_id": 5
}
```

**Headers:**
```
Authorization: Bearer <token>
```

#### DELETE `/likes/{profile_id}`
**Описание:** Убрать лайк с профиля

**Headers:**
```
Authorization: Bearer <token>
```

#### GET `/likes/my-likes`
**Описание:** Получить список профилей, которые лайкнул текущий пользователь

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 5,
    "name": "Маша",
    "age": 26,
    "gender": "female",
    "city": "Казань",
    "bio": "Кондитер, пеку торты",
    "photo_url": "https://example.com/photo.jpg",
    "contact_info": "@masha_cakes",
    "tags": ["выпечка", "кулинария"]
  }
]
```

#### GET `/likes/who-liked-me`
**Описание:** Получить список профилей, которые лайкнули текущего пользователя

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** Аналогичен `/likes/my-likes`

### Пользователи

#### GET `/users/me`
**Описание:** Получить информацию о текущем пользователе

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2025-12-23T14:42:00"
}
```

## Фронтенд Функции

### Аутентификация

```javascript
// Регистрация
await registerUser(email, password);

// Вход
await loginUser(email, password);

// Выход
logoutUser();
```

### Работа с профилями

```javascript
// Загрузить профили с фильтрами
await loadProfiles();

// Создать профиль
await createProfile(profileData);

// Обновить профиль
await updateProfile(profileId, profileData);
```

### Лайки

```javascript
// Лайкнуть профиль
await likeProfile(profile);

// Убрать лайк
await unlikeProfile(profile);

// Получить лайкнутые профили
await getLikedProfiles();

// Получить кто лайкнул меня
await getWhoLikedMe();
```

## Локальное хранилище

### Сохраняемые данные

- `authToken` - JWT токен для авторизации
- `darkMode` - Настройка темной темы ('0' или '1')

### Удаленные данные (теперь в БД)

- ~~`currentUser`~~ → Теперь `/users/me`
- ~~`likes_${email}`~~ → Теперь `/likes/my-likes`
- ~~`viewedProfiles_${email}`~~ → Управляется на фронтенде
- ~~`likedBy_${profileId}`~~ → Теперь `/likes/who-liked-me`

## Обработка ошибок

```javascript
try {
  const data = await apiRequest('/endpoint');
  // Обработка данных
} catch (error) {
  if (error.message === 'Необходима авторизация') {
    // Показать форму входа
    authPanel.setAttribute('aria-hidden', 'false');
  } else {
    // Показать уведомление об ошибке
    showNotification(error.message);
  }
}
```

## Запуск приложения

### Backend

```bash
# Установка зависимостей
pip install -r requirements.txt

# Инициализация базы данных
python init_db.py

# Запуск сервера
python main.py
```

Сервер будет доступен на `http://localhost:8001`

### Frontend

Просто откройте `http://localhost:8001` в браузере.

## Особенности реализации

### 1. Автоматическая авторизация

При загрузке страницы проверяется наличие токена в localStorage. Если токен есть, автоматически запрашивается информация о пользователе.

```javascript
window.addEventListener('DOMContentLoaded', async () => {
  if (authToken) {
    try {
      currentUser = await apiRequest('/users/me');
    } catch (error) {
      // Токен невалиден - очистить
      authToken = null;
      localStorage.removeItem('authToken');
    }
  }
  updateAuthUI();
  await loadProfiles();
});
```

### 2. Фильтрация профилей

Фильтры по городу и полу отправляются как query параметры к API:

```javascript
const selectedCity = cityFilter.value;
const selectedGender = genderFilter.value;

profiles = await fetchProfiles(
  selectedCity !== 'all' ? selectedCity : null,
  selectedGender !== 'all' ? selectedGender : null
);
```

### 3. Просмотренные профили

Массив `viewedProfiles` хранится локально на фронтенде и используется для фильтрации уже просмотренных карточек:

```javascript
if (currentUser && viewedProfiles.length > 0) {
  profiles = profiles.filter(profile => !viewedProfiles.includes(profile.id));
}
```

### 4. Темная тема

Тема переключается через класс `dark` на элементе `<html>` и сохраняется в localStorage:

```javascript
function applyTheme() {
  if (darkMode) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
}
```

## Улучшения по сравнению с оригиналом

### 1. Разделение на модули
- HTML, CSS и JS теперь в отдельных файлах
- Легче поддерживать и расширять код
- Возможность кеширования статических файлов

### 2. Интеграция с базой данных
- Данные хранятся в SQLite вместо localStorage
- Синхронизация между устройствами
- Поддержка многопользовательского режима

### 3. Аутентификация
- JWT токены для безопасной авторизации
- Защищенные API endpoints
- Автоматическое обновление токена

### 4. API-first подход
- Четкое разделение frontend и backend
- Возможность создания мобильных приложений
- RESTful архитектура

### 5. Обработка ошибок
- Централизованная обработка ошибок API
- Уведомления пользователю о проблемах
- Автоматический логаут при невалидном токене

## Дальнейшие улучшения

1. **Загрузка изображений**: Добавить эндпоинт для загрузки фото на сервер
2. **Пагинация**: Реализовать ленивую загрузку профилей
3. **Поиск**: Добавить полнотекстовый поиск по профилям
4. **Мэтчи**: Уведомления о взаимных лайках
5. **Чат**: Система сообщений между пользователями
6. **Валидация**: Расширенная валидация данных на backend
7. **Тесты**: Unit и integration тесты для API
8. **WebSocket**: Реал-тайм обновления для лайков и сообщений
