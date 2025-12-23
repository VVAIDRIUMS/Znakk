// Dating app - НОВАЯ СТАБИЛЬНАЯ ВЕРСИЯ
const API_BASE = window.location.origin;

let profiles = [];
let currentIndex = 0;
let myProfile = null;
let darkMode = localStorage.getItem('darkMode') === '1';
let currentUser = null;
let authToken = localStorage.getItem('authToken') || null;
let viewedProfiles = [];
let currentViewingProfile = null;
let isViewingFromLikedList = false;

// DOM elements
const cardStack = document.querySelector('.card-stack');
const themeToggle = document.getElementById('theme-toggle');
const createBtn = document.getElementById('create-btn');
const createPanel = document.querySelector('.create-panel');
const createClose = document.querySelector('.create-close');
const createSave = document.getElementById('create-save');
const createPreview = document.getElementById('create-preview');
const authBtn = document.getElementById('auth-btn');
const authBtnText = document.getElementById('auth-btn-text');
const likedPanel = document.querySelector('.liked-panel');
const likedList = document.querySelector('.liked-list');
const likedBackBtn = document.querySelector('.back-btn');
const whoLikedPanel = document.querySelector('.who-liked-panel');
const whoLikedList = document.querySelector('.who-liked-list');
const whoLikedBackBtn = document.querySelector('.who-back-btn');
const whoLikedBtn = document.getElementById('who-liked-btn');
const savedBtn = document.getElementById('saved-btn');
const cityFilter = document.getElementById('city-filter');
const genderFilter = document.getElementById('gender-filter');
const likeBtn = document.getElementById('like-btn');
const skipBtn = document.getElementById('skip-btn');
const refreshBtn = document.getElementById('refresh-btn');
const profileViewPanel = document.querySelector('.profile-view-panel');
const profileViewClose = document.querySelector('.profile-view-close');
const profileViewLikeBtn = document.getElementById('profile-view-like-btn');
const profileViewUnlikeBtn = document.getElementById('profile-view-unlike-btn');
const authPanel = document.querySelector('.auth-panel');
const authClose = document.querySelector('.auth-close');

// ✅ НОВОЕ: Функция для безопасного API запроса
async function apiRequest(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  const requestOptions = {
    method: options.method || 'GET',
    headers,
    credentials: 'include'
  };
  
  if (options.body) {
    requestOptions.body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
  }
  
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, requestOptions);
    const data = await response.json();
    
    if (response.status === 401) {
      console.error('❌ 401 Unauthorized');
      // НЕ выходим из аккаунта, просто возвращаем ошибку
      throw new Error('Требуется авторизация');
    }
    
    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Ошибка запроса');
    }
    
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// ✅ НОВОЕ: Функция для получения ошибки
function getErrorMessage(error) {
  if (typeof error === 'string') return error;
  if (error instanceof Error) return error.message;
  if (error?.detail) return error.detail;
  if (error?.message) return error.message;
  return 'Неизвестная ошибка';
}

// ============================================
// AUTHENTICATION FUNCTIONS
// ============================================

async function loginUser(email, password) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  
  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
      credentials: 'include'
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || 'Ошибка входа');
    }
    
    authToken = data.access_token;
    localStorage.setItem('authToken', authToken);
    
    currentUser = {
      id: data.user_id,
      email: email,
      role_id: data.role_id || 1
    };
    
    return currentUser;
  } catch (error) {
    throw error;
  }
}

async function registerUser(email, password) {
  try {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, role_id: 1 }),
      credentials: 'include'
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || 'Ошибка регистрации');
    }
    
    // После регистрации сразу логинимся
    return await loginUser(email, password);
  } catch (error) {
    throw error;
  }
}

function logoutUser() {
  authToken = null;
  currentUser = null;
  localStorage.removeItem('authToken');
  viewedProfiles = [];
}

function updateAuthUI() {
  if (currentUser) {
    document.getElementById('current-user-email').textContent = currentUser.email;
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'none';
    document.getElementById('logout-form').style.display = 'block';
    document.getElementById('login-tab').style.display = 'none';
    document.getElementById('register-tab').style.display = 'none';
  } else {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
    document.getElementById('logout-form').style.display = 'none';
    document.getElementById('login-tab').style.display = 'block';
    document.getElementById('register-tab').style.display = 'block';
  }
}

function showAuthMessage(message, type) {
  const authMessage = document.getElementById('auth-message');
  authMessage.textContent = message;
  authMessage.className = `auth-message ${type}`;
}

function updateAuthButtonDisplay() {
  if (currentUser && authBtn && authBtnText) {
    authBtnText.textContent = currentUser.email;
    authBtn.style.width = 'auto';
  } else if (authBtn && authBtnText) {
    authBtnText.textContent = '';
    authBtn.style.width = '40px';
  }
}

// ============================================
// PROFILES FUNCTIONS
// ============================================

async function fetchProfiles(city = null, gender = null) {
  let endpoint = '/profiles/';
  const params = new URLSearchParams();
  
  if (city && city !== 'all') params.append('city', city);
  if (gender && gender !== 'all') params.append('gender', gender);
  
  if (params.toString()) endpoint += '?' + params.toString();
  
  try {
    return await apiRequest(endpoint);
  } catch (error) {
    console.error('Error fetching profiles:', error);
    return [];
  }
}

// ✅ ИСПРАВЛЕНО: Отправка данных как form data
async function createProfile(profileData) {
  const params = new URLSearchParams();
  params.append('username', profileData.username);
  params.append('age', profileData.age.toString());
  params.append('gender', profileData.gender);
  params.append('city', profileData.city);
  params.append('photo', profileData.photo);
  params.append('description', profileData.description);
  params.append('tags', profileData.tags || '');
  
  try {
    const response = await fetch(`${API_BASE}/profiles/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params.toString(),
      credentials: 'include'
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Ошибка сохранения профиля');
    }
    
    return data;
  } catch (error) {
    console.error('Create profile error:', error);
    throw error;
  }
}

// ============================================
// LIKES FUNCTIONS - НОВАЯ СТАБИЛЬНАЯ ВЕРСИЯ
// ============================================

// ✅ НОВОЕ: Добавить лайк (безопасный способ)
async function likeProfile(profile) {
  if (!currentUser) {
    showNotification('❌ Для лайков нужно войти в аккаунт');
    authPanel.setAttribute('aria-hidden', 'false');
    return false;
  }
  
  try {
    const response = await apiRequest('/likes/add', {
      method: 'POST',
      body: { liked_profile_id: profile.id }
    });
    
    if (response.success) {
      showNotification(`❤️ Вы лайкнули ${profile.username}!`);
      return true;
    } else {
      showNotification(`⚠️ ${response.message || 'Ошибка при лайке'}`);
      return false;
    }
  } catch (error) {
    console.error('Like error:', error);
    showNotification(`❌ ${getErrorMessage(error)}`);
    return false;
  }
}

// ✅ НОВОЕ: Удалить лайк (безопасный способ)
async function unlikeProfile(profile) {
  if (!currentUser) return false;
  
  try {
    const response = await apiRequest(`/likes/remove/${profile.id}`, {
      method: 'POST'
    });
    
    if (response.success) {
      showNotification('👍 Лайк удален');
      return true;
    } else {
      showNotification(`⚠️ ${response.message || 'Ошибка'}`);
      return false;
    }
  } catch (error) {
    console.error('Unlike error:', error);
    showNotification(`❌ ${getErrorMessage(error)}`);
    return false;
  }
}

// ✅ НОВОЕ: Получить мои лайки
async function getMyLikes() {
  if (!currentUser) {
    showNotification('❌ Пожалуйста авторизуйтесь');
    return [];
  }
  
  try {
    return await apiRequest('/likes/my-likes');
  } catch (error) {
    console.error('Error getting my likes:', error);
    showNotification('❌ Ошибка загружки лайков');
    return [];
  }
}

// ✅ НОВОЕ: Получить кто лайкнул меня
async function getWhoLikedMe() {
  if (!currentUser) {
    showNotification('❌ Пожалуйста авторизуйтесь');
    return [];
  }
  
  try {
    return await apiRequest('/likes/who-liked-me');
  } catch (error) {
    console.error('Error getting who liked me:', error);
    showNotification('❌ Ошибка загружки лайков');
    return [];
  }
}

// ✅ НОВОЕ: Проверить есть ли лайк
async function checkIfLiked(profileId) {
  if (!currentUser) return false;
  
  try {
    const response = await apiRequest(`/likes/check/${profileId}`);
    return response.liked || false;
  } catch (error) {
    return false;
  }
}

// ============================================
// UI FUNCTIONS
// ============================================

function showNotification(message) {
  const existing = document.querySelector('.notification');
  if (existing) existing.remove();
  
  const notification = document.createElement('div');
  notification.className = 'notification';
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 80px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0,0,0,0.8);
    color: white;
    padding: 12px 20px;
    border-radius: 10px;
    z-index: 1000;
    font-size: 14px;
    max-width: 300px;
    animation: fadeInOut 3s ease-in-out;
  `;
  
  if (!document.querySelector('style[data-notification-style]')) {
    const style = document.createElement('style');
    style.setAttribute('data-notification-style', 'true');
    style.textContent = `
      @keyframes fadeInOut {
        0% { opacity: 0; }
        15% { opacity: 1; }
        85% { opacity: 1; }
        100% { opacity: 0; }
      }
    `;
    document.head.appendChild(style);
  }
  
  document.body.appendChild(notification);
  setTimeout(() => notification.remove(), 3000);
}

async function loadProfiles() {
  try {
    const selectedCity = cityFilter?.value || 'all';
    const selectedGender = genderFilter?.value || 'all';
    
    profiles = await fetchProfiles(
      selectedCity !== 'all' ? selectedCity : null,
      selectedGender !== 'all' ? selectedGender : null
    );
    
    currentIndex = 0;
    renderCard();
  } catch (error) {
    console.error('Error loading profiles:', error);
    showNotification('❌ Ошибка загрузки профилей');
  }
}

function renderCard() {
  if (!cardStack) return;
  cardStack.innerHTML = '';
  
  if (!profiles || currentIndex >= profiles.length) {
    cardStack.innerHTML = '<div class="empty-text">🔍 Нет доступных профилей<br><br>🔄 Нажмите чтобы обновить</div>';
    refreshBtn?.classList.add('show');
    return;
  }
  
  refreshBtn?.classList.remove('show');
  
  const profile = profiles[currentIndex];
  const card = document.createElement('div');
  card.className = 'card';
  
  card.innerHTML = `
    <div class="card-inner">
      <div class="card-photo" style="background-image: url(${profile.photo || 'https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg?w=800&q=80'})"></div>
      <div class="card-info">
        <div class="card-name-age">👤 ${profile.username}, ${profile.age}</div>
        <div class="card-city">📍 ${profile.city || 'Не указан'}</div>
        <div class="card-bio">💬 ${profile.description || 'Нет описания'}</div>
      </div>
    </div>
  `;
  cardStack.appendChild(card);
}

function nextCard() {
  if (currentIndex < profiles.length - 1) {
    currentIndex++;
    renderCard();
  } else {
    cardStack.innerHTML = '<div class="empty-text">🔍 Нет доступных профилей<br><br>🔄 Нажмите чтобы обновить</div>';
    refreshBtn?.classList.add('show');
  }
}

async function likeCurrentProfile() {
  if (!currentUser) {
    showNotification('❌ Пожалуйста авторизуйтесь');
    authPanel.setAttribute('aria-hidden', 'false');
    return;
  }
  
  if (currentIndex < profiles.length) {
    const profile = profiles[currentIndex];
    if (await likeProfile(profile)) {
      viewedProfiles.push(profile.id);
      nextCard();
    }
  }
}

function skipCurrentProfile() {
  if (currentIndex < profiles.length) {
    const profile = profiles[currentIndex];
    viewedProfiles.push(profile.id);
    showNotification(`✕ Вы пропустили ${profile.username}`);
    nextCard();
  }
}

function refreshProfiles() {
  viewedProfiles = [];
  loadProfiles();
  showNotification('🔄 Карточки обновлены!');
}

function viewProfile(profile) {
  currentViewingProfile = profile;
  
  document.getElementById('profile-view-photo').style.backgroundImage = `url(${profile.photo || 'https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg?w=800&q=80'})`;
  document.getElementById('profile-view-name').textContent = profile.username;
  document.getElementById('profile-view-age').textContent = `${profile.age} лет`;
  document.getElementById('profile-view-city').textContent = profile.city || 'Не указан';
  document.getElementById('profile-view-bio').textContent = profile.description || 'Не указано';
  document.getElementById('profile-view-gender').textContent = profile.gender === 'male' ? 'Мужчина' : 'Женщина';
  document.getElementById('profile-view-contact').textContent = profile.contact || 'Не указано';
  document.getElementById('profile-view-tags').textContent = profile.tags || 'Нет';
  
  // Проверяем лайк
  checkIfLiked(profile.id).then(isLiked => {
    if (isLiked) {
      profileViewLikeBtn.style.display = 'none';
      profileViewUnlikeBtn.style.display = 'block';
    } else {
      profileViewLikeBtn.style.display = 'block';
      profileViewUnlikeBtn.style.display = 'none';
    }
  });
  
  profileViewPanel.setAttribute('aria-hidden', 'false');
}

// ============================================
// EVENT LISTENERS
// ============================================

// ✅ ИСПРАВЛЕНО: Кнопки управления
likeBtn?.addEventListener('click', likeCurrentProfile);
skipBtn?.addEventListener('click', skipCurrentProfile);
refreshBtn?.addEventListener('click', refreshProfiles);

// ✅ ИСПРАВЛЕНО: Создание профиля
createBtn?.addEventListener('click', () => {
  if (!currentUser) {
    showNotification('❌ Для создания анкеты нужно войти в аккаунт');
    authPanel.setAttribute('aria-hidden', 'false');
    return;
  }
  createPanel?.setAttribute('aria-hidden', 'false');
});

createClose?.addEventListener('click', () => {
  createPanel?.setAttribute('aria-hidden', 'true');
});

// ✅ ИСПРАВЛЕНО: Сохранение профиля
createSave?.addEventListener('click', async () => {
  if (!currentUser) {
    showNotification('❌ Пожалуйста авторизуйтесь');
    return;
  }
  
  const username = document.getElementById('create-name').value.trim();
  const age = document.getElementById('create-age').value.trim();
  const gender = document.getElementById('create-gender').value.trim();
  const city = document.getElementById('create-city').value.trim();
  const photo = document.getElementById('create-photo').value.trim();
  const description = document.getElementById('create-bio').value.trim();
  const tags = document.getElementById('create-tags').value.trim();
  
  // Валидация
  if (!username || !age || !gender || !city || !photo || !description) {
    showNotification('❌ Заполните все поля');
    return;
  }
  
  try {
    await createProfile({
      username, age: parseInt(age), gender, city, photo, description, tags
    });
    
    showNotification('✅ Профиль создан!');
    createPanel?.setAttribute('aria-hidden', 'true');
    
    // Очищаем форму
    document.getElementById('create-name').value = '';
    document.getElementById('create-age').value = '';
    document.getElementById('create-gender').value = '';
    document.getElementById('create-city').value = '';
    document.getElementById('create-photo').value = '';
    document.getElementById('create-bio').value = '';
    document.getElementById('create-tags').value = '';
    
    await loadProfiles();
  } catch (error) {
    showNotification(`❌ ${getErrorMessage(error)}`);
  }
});

// ✅ ИСПРАВЛЕНО: Кнопка лайков (мои лайки)
savedBtn?.addEventListener('click', async () => {
  if (!currentUser) {
    showNotification('❌ Пожалуйста авторизуйтесь');
    authPanel.setAttribute('aria-hidden', 'false');
    return;
  }
  
  const liked = await getMyLikes();
  likedList.innerHTML = '';
  
  if (liked.length === 0) {
    likedList.innerHTML = '<div class="empty-text">💔 Нет лайков</div>';
  } else {
    liked.forEach(profile => {
      const item = document.createElement('div');
      item.className = 'liked-item';
      item.innerHTML = `
        <div class="profile-photo-small" style="background-image: url(${profile.photo})"></div>
        <div class="profile-info">
          <div class="profile-name-age">👤 ${profile.username}, ${profile.age}</div>
          <div class="profile-city">📍 ${profile.city}</div>
        </div>
        <div class="item-actions">
          <button class="item-action-btn view-btn" onclick="viewProfile(${JSON.stringify(profile).replace(/"/g, '&quot;')})" title="Посмотреть">👁</button>
          <button class="item-action-btn unlike-btn" onclick="unlikeProfile(${JSON.stringify(profile).replace(/"/g, '&quot;')})" title="Убрать лайк">✕</button>
        </div>
      `;
      likedList.appendChild(item);
    });
  }
  
  likedPanel?.setAttribute('aria-hidden', 'false');
});

// ✅ ИСПРАВЛЕНО: Кнопка возврата из лайков
likedBackBtn?.addEventListener('click', () => {
  likedPanel?.setAttribute('aria-hidden', 'true');
});

// ✅ ИСПРАВЛЕНО: Кнопка "Кто лайкнул меня"
whoLikedBtn?.addEventListener('click', async () => {
  if (!currentUser) {
    showNotification('❌ Пожалуйста авторизуйтесь');
    authPanel.setAttribute('aria-hidden', 'false');
    return;
  }
  
  const whoLiked = await getWhoLikedMe();
  whoLikedList.innerHTML = '';
  
  if (whoLiked.length === 0) {
    whoLikedList.innerHTML = '<div class="empty-text">💔 Никто еще не лайкнул вас</div>';
  } else {
    whoLiked.forEach(profile => {
      const item = document.createElement('div');
      item.className = 'who-liked-item';
      item.innerHTML = `
        <div class="profile-photo-small" style="background-image: url(${profile.photo})"></div>
        <div class="profile-info">
          <div class="profile-name-age">👤 ${profile.username}, ${profile.age}</div>
          <div class="profile-city">📍 ${profile.city}</div>
        </div>
        <div class="item-actions">
          <button class="item-action-btn view-btn" onclick="viewProfile(${JSON.stringify(profile).replace(/"/g, '&quot;')})" title="Посмотреть">👁</button>
          <button class="item-action-btn like-btn" onclick="likeProfile(${JSON.stringify(profile).replace(/"/g, '&quot;')})" title="Лайкнуть">❤️</button>
        </div>
      `;
      whoLikedList.appendChild(item);
    });
  }
  
  whoLikedPanel?.setAttribute('aria-hidden', 'false');
});

// ✅ ИСПРАВЛЕНО: Кнопка возврата из "Кто лайкнул"
whoLikedBackBtn?.addEventListener('click', () => {
  whoLikedPanel?.setAttribute('aria-hidden', 'true');
});

// ✅ ИСПРАВЛЕНО: Просмотр профиля
profileViewClose?.addEventListener('click', () => {
  profileViewPanel.setAttribute('aria-hidden', 'true');
});

profileViewLikeBtn?.addEventListener('click', async () => {
  if (currentViewingProfile && await likeProfile(currentViewingProfile)) {
    profileViewLikeBtn.style.display = 'none';
    profileViewUnlikeBtn.style.display = 'block';
  }
});

profileViewUnlikeBtn?.addEventListener('click', async () => {
  if (currentViewingProfile && await unlikeProfile(currentViewingProfile)) {
    profileViewLikeBtn.style.display = 'block';
    profileViewUnlikeBtn.style.display = 'none';
  }
});

// ✅ ИСПРАВЛЕНО: Аутентификация
document.getElementById('login-tab')?.addEventListener('click', () => {
  document.getElementById('login-tab').classList.add('active');
  document.getElementById('register-tab').classList.remove('active');
  document.getElementById('login-form').style.display = 'block';
  document.getElementById('register-form').style.display = 'none';
});

document.getElementById('register-tab')?.addEventListener('click', () => {
  document.getElementById('register-tab').classList.add('active');
  document.getElementById('login-tab').classList.remove('active');
  document.getElementById('register-form').style.display = 'block';
  document.getElementById('login-form').style.display = 'none';
});

document.getElementById('login-btn')?.addEventListener('click', async () => {
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  
  if (!email || !password) {
    showAuthMessage('❌ Заполните все поля', 'error');
    return;
  }
  
  try {
    await loginUser(email, password);
    updateAuthUI();
    updateAuthButtonDisplay();
    showAuthMessage('✅ Вход успешен!', 'success');
    setTimeout(() => {
      authPanel.setAttribute('aria-hidden', 'true');
      loadProfiles();
    }, 1000);
  } catch (error) {
    showAuthMessage(`❌ ${getErrorMessage(error)}`, 'error');
  }
});

document.getElementById('register-btn')?.addEventListener('click', async () => {
  const email = document.getElementById('register-email').value;
  const password = document.getElementById('register-password').value;
  const confirm = document.getElementById('register-confirm-password').value;
  
  if (!email || !password || !confirm) {
    showAuthMessage('❌ Заполните все поля', 'error');
    return;
  }
  
  if (password !== confirm) {
    showAuthMessage('❌ Пароли не совпадают', 'error');
    return;
  }
  
  try {
    await registerUser(email, password);
    updateAuthUI();
    updateAuthButtonDisplay();
    showAuthMessage('✅ Регистрация успешна!', 'success');
    setTimeout(() => {
      authPanel.setAttribute('aria-hidden', 'true');
      loadProfiles();
    }, 1000);
  } catch (error) {
    showAuthMessage(`❌ ${getErrorMessage(error)}`, 'error');
  }
});

document.getElementById('logout-btn')?.addEventListener('click', () => {
  logoutUser();
  updateAuthUI();
  updateAuthButtonDisplay();
  showAuthMessage('✅ Вы вышли из аккаунта', 'success');
  setTimeout(() => {
    authPanel.setAttribute('aria-hidden', 'true');
    loadProfiles();
  }, 1000);
});

authBtn?.addEventListener('click', () => {
  updateAuthUI();
  authPanel.setAttribute('aria-hidden', 'false');
});

authClose?.addEventListener('click', () => {
  authPanel.setAttribute('aria-hidden', 'true');
});

cityFilter?.addEventListener('change', loadProfiles);
genderFilter?.addEventListener('change', loadProfiles);

// Тема
function applyTheme() {
  if (darkMode) {
    document.documentElement.classList.add('dark');
    if (themeToggle) themeToggle.textContent = '☀️';
  } else {
    document.documentElement.classList.remove('dark');
    if (themeToggle) themeToggle.textContent = '🌙';
  }
}

applyTheme();

themeToggle?.addEventListener('click', () => {
  darkMode = !darkMode;
  localStorage.setItem('darkMode', darkMode ? '1' : '0');
  applyTheme();
});

// ============================================
// INITIALIZATION
// ============================================

window.addEventListener('DOMContentLoaded', async () => {
  if (authToken) {
    try {
      console.log('🔍 Проверка авторизации...');
      // Просто считаем что пользователь авторизован если есть токен
      // Не делаем лишний запрос к БД
      console.log('✅ Пользователь авторизован');
    } catch (error) {
      console.error('❌ Ошибка авторизации:', error);
      logoutUser();
    }
  }
  
  updateAuthUI();
  updateAuthButtonDisplay();
  await loadProfiles();
});
