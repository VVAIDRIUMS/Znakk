// Dating app with API integration
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
const authBtn = document.getElementById('auth-btn');
const authBtnText = document.getElementById('auth-btn-text');
const likedPanel = document.querySelector('.liked-panel');
const likedList = document.querySelector('.liked-list');
const whoLikedPanel = document.querySelector('.who-liked-panel');
const whoLikedList = document.querySelector('.who-liked-list');
const whoLikedBtn = document.getElementById('who-liked-btn');
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
const userStatus = document.getElementById('user-status');
const userStatusEmail = document.getElementById('user-status-email');
const logoutHeaderBtn = document.getElementById('logout-header-btn');

// Helper function to convert error to string
function getErrorMessage(error) {
  if (typeof error === 'string') {
    return error;
  }
  if (error instanceof Error) {
    return error.message || 'Unknown error';
  }
  if (error && typeof error === 'object') {
    if (error.detail) return error.detail;
    if (error.message) return error.message;
    return JSON.stringify(error);
  }
  return String(error) || 'Unknown error';
}

// API Functions
async function apiRequest(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }
  
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers
    });
    
    if (response.status === 401) {
      // ✅ МОННато - правильная обработка 401
      console.error('✅ 401 Unauthorized for endpoint:', endpoint);
      console.error('Token preview:', authToken ? authToken.substring(0, 20) + '...' : 'No token');
      
      // Unauthorized - clear token and show auth
      authToken = null;
      currentUser = null;
      localStorage.removeItem('authToken');
      updateAuthUI();
      updateAuthButtonDisplay();
      updateUserStatusDisplay();
      
      // Показываю ошибку пользователю
      showNotification('Сессия истекла. Пожалуйста, войдите снова');
      authPanel.setAttribute('aria-hidden', 'false');
      
      throw new Error('Токен не активен или истек');
    }
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || 'Ошибка запроса');
    }
    
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// Auth API
async function loginUser(email, password) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  
  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      const errorMessage = data.detail || data.message || 'Ошибка входа';
      throw new Error(errorMessage);
    }
    
    // ✅ Отработано токена
    authToken = data.access_token;
    console.log('✅ Token received and saved');
    console.log('Token preview:', authToken.substring(0, 20) + '...');
    localStorage.setItem('authToken', authToken);
    
    // ✅ НОВОЕ - заполним основные данные из токена
    currentUser = {
      id: data.user_id,
      email: email,
      role_id: data.role_id
    };
    
    // Попытаюсь понять полные данные
    try {
      const fullUser = await apiRequest('/users/me');
      currentUser = fullUser;
      console.log('✅ User data loaded from /users/me');
    } catch (userError) {
      console.warn('⚠️  Could not load full user data:', userError);
      // Мы все равно вошли!
    }
    
    return currentUser;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

async function registerUser(email, password) {
  const user = await apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password , role_id: 1 })
  });
  
  // Auto-login after registration
  return await loginUser(email, password);
}

function logoutUser() {
  authToken = null;
  currentUser = null;
  localStorage.removeItem('authToken');
  viewedProfiles = [];
}

// ✅ НОВОЕ - функция обновления кнопки входа
function updateAuthButtonDisplay() {
  if (currentUser && authBtn && authBtnText) {
    // Когда вошли
    authBtnText.textContent = currentUser.email;
    authBtn.style.width = 'auto';
  } else if (authBtn && authBtnText) {
    // Когда не вошли
    authBtnText.textContent = '';
    authBtn.style.width = '40px';
  }
}

// ✅ НОВОЕ - функция обновления статуса пользователя в хедере
function updateUserStatusDisplay() {
  if (currentUser && userStatus && userStatusEmail && logoutHeaderBtn) {
    userStatusEmail.textContent = currentUser.email;
    userStatus.style.display = 'flex';
    if (authBtn) authBtn.style.display = 'none';
  } else if (userStatus && authBtn) {
    userStatus.style.display = 'none';
    if (authBtn) authBtn.style.display = 'flex';
  }
}

// ✅ НОВОЕ - кнопка выхода в хедере
if (logoutHeaderBtn) {
  logoutHeaderBtn.addEventListener('click', () => {
    logoutUser();
    updateAuthUI();
    updateAuthButtonDisplay();
    updateUserStatusDisplay();
    showNotification('Вы вышли из аккаунта');
    loadProfiles();
  });
}

// Profiles API
async function fetchProfiles(city = null, gender = null) {
  let endpoint = '/profiles/';
  const params = new URLSearchParams();
  
  if (city && city !== 'all') {
    params.append('city', city);
  }
  
  if (gender && gender !== 'all') {
    params.append('gender', gender);
  }
  
  if (params.toString()) {
    endpoint += '?' + params.toString();
  }
  
  try {
    return await apiRequest(endpoint);
  } catch (error) {
    console.error('Error fetching profiles:', error);
    // Fallback to demo endpoint if API fails
    const response = await fetch('/api/profiles');
    return await response.json();
  }
}

async function createProfile(profileData) {
  return await apiRequest('/profiles/', {
    method: 'POST',
    body: JSON.stringify(profileData)
  });
}

async function updateProfile(profileId, profileData) {
  return await apiRequest(`/profiles/${profileId}`, {
    method: 'PUT',
    body: JSON.stringify(profileData)
  });
}

// Likes API
async function likeProfileAPI(profileId) {
  return await apiRequest('/likes/', {
    method: 'POST',
    body: JSON.stringify({ liked_profile_id: profileId })
  });
}

async function unlikeProfileAPI(profileId) {
  return await apiRequest(`/likes/${profileId}`, {
    method: 'DELETE'
  });
}

async function getLikedProfiles() {
  try {
    return await apiRequest('/likes/my-likes');
  } catch (error) {
    console.error('Error fetching liked profiles:', error);
    return [];
  }
}

async function getWhoLikedMe() {
  try {
    return await apiRequest('/likes/who-liked-me');
  } catch (error) {
    console.error('Error fetching who liked me:', error);
    return [];
  }
}

// Load profiles
async function loadProfiles() {
  try {
    const selectedCity = cityFilter.value;
    const selectedGender = genderFilter.value;
    
    profiles = await fetchProfiles(
      selectedCity !== 'all' ? selectedCity : null,
      selectedGender !== 'all' ? selectedGender : null
    );
    
    // Filter out viewed profiles
    if (currentUser && viewedProfiles.length > 0) {
      profiles = profiles.filter(profile => !viewedProfiles.includes(profile.id));
    }
    
    currentIndex = 0;
    renderCard();
  } catch (error) {
    console.error('Error loading profiles:', error);
    showNotification('Ошибка загрузки профилей');
  }
}

// Render current card
function renderCard() {
  if (!cardStack) return;
  cardStack.innerHTML = '';
  
  if (currentIndex >= profiles.length) {
    cardStack.innerHTML = '<div class="empty-text">Нет доступных профилей<br><br>Нажмите 🔄 чтобы обновить</div>';
    refreshBtn.classList.add('show');
    return;
  }
  
  refreshBtn.classList.remove('show');
  
  const profile = profiles[currentIndex];
  const card = document.createElement('div');
  card.className = 'card';
  
  const genderEmoji = profile.gender === 'male' ? '🚮' : profile.gender === 'female' ? '🚮' : '';
  
  card.innerHTML = `
    <div class="card-inner">
      <div class="card-photo" style="background-image: url(${profile.photo_url || 'https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg?w=800&q=80'})"></div>
      <div class="card-info">
        <div class="card-name-age">${genderEmoji} ${profile.name}, ${profile.age}</div>
        <div class="card-city">${profile.city || ''}</div>
        <div class="card-bio">${profile.bio || ''}</div>
      </div>
    </div>
  `;
  cardStack.appendChild(card);
}

// Next card
function nextCard() {
  if (currentIndex < profiles.length - 1) {
    currentIndex++;
    renderCard();
  } else {
    cardStack.innerHTML = '<div class="empty-text">Нет доступных профилей<br><br>Нажмите 🔄 чтобы обновить</div>';
    refreshBtn.classList.add('show');
  }
}

// Refresh profiles
function refreshProfiles() {
  viewedProfiles = [];
  currentIndex = 0;
  loadProfiles();
  showNotification('Карточки обновлены!');
}

// Like current profile
async function likeCurrentProfile() {
  if (currentIndex < profiles.length) {
    const profile = profiles[currentIndex];
    await likeProfile(profile);
    
    // Mark as viewed
    viewedProfiles.push(profile.id);
    
    nextCard();
  }
}

// Like a specific profile
async function likeProfile(profile) {
  if (!currentUser) {
    showAuthMessage('Для лайков нужно войти в аккаунт', 'error');
    authPanel.setAttribute('aria-hidden', 'false');
    return false;
  }
  
  try {
    await likeProfileAPI(profile.id);
    
    // Animation effect
    if (likeBtn) {
      likeBtn.style.transform = 'scale(1.2)';
      likeBtn.style.backgroundColor = '#34c759';
      likeBtn.style.color = 'white';
      
      setTimeout(() => {
        likeBtn.style.transform = 'scale(1)';
        likeBtn.style.backgroundColor = '';
        likeBtn.style.color = '';
      }, 300);
    }
    
    showNotification(`Вы лайкнули ${profile.name}!`);
    return true;
  } catch (error) {
    console.error('Error liking profile:', error);
    showNotification('Ошибка при лайке');
    return false;
  }
}

// Unlike a profile
async function unlikeProfile(profile) {
  if (!currentUser) return false;
  
  try {
    await unlikeProfileAPI(profile.id);
    showNotification(`Лайк для ${profile.name} убран`);
    return true;
  } catch (error) {
    console.error('Error unliking profile:', error);
    showNotification('Ошибка при снятии лайка');
    return false;
  }
}

// Skip current profile
function skipCurrentProfile() {
  if (currentIndex < profiles.length) {
    const profile = profiles[currentIndex];
    
    // Mark as viewed
    viewedProfiles.push(profile.id);
    
    // Animation effect
    if (skipBtn) {
      skipBtn.style.transform = 'scale(1.2)';
      skipBtn.style.backgroundColor = '#ff3b30';
      skipBtn.style.color = 'white';
      
      setTimeout(() => {
        skipBtn.style.transform = 'scale(1)';
        skipBtn.style.backgroundColor = '';
        skipBtn.style.color = '';
      }, 300);
    }
    
    showNotification(`Вы пропустили ${profile.name}`);
    nextCard();
  }
}

// Show notification
function showNotification(message) {
  const existingNotification = document.querySelector('.notification');
  if (existingNotification) {
    existingNotification.remove();
  }
  
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
    animation: fadeInOut 3s ease-in-out;
  `;
  
  if (!document.querySelector('style[data-notification-style]')) {
    const style = document.createElement('style');
    style.setAttribute('data-notification-style', 'true');
    style.textContent = `
      @keyframes fadeInOut {
        0% { opacity: 0; transform: translateX(-50%) translateY(-20px); }
        15% { opacity: 1; transform: translateX(-50%) translateY(0); }
        85% { opacity: 1; transform: translateX(-50%) translateY(0); }
        100% { opacity: 0; transform: translateX(-50%) translateY(-20px); }
      }
    `;
    document.head.appendChild(style);
  }
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    if (notification.parentNode) {
      notification.remove();
    }
  }, 3000);
}

// Swipe handlers
let startX = 0;
if (cardStack) {
  cardStack.addEventListener('touchstart', (e) => {
    startX = e.touches[0].clientX;
  });
  
  cardStack.addEventListener('touchend', (e) => {
    const endX = e.changedTouches[0].clientX;
    const diff = endX - startX;
    if (Math.abs(diff) > 100) {
      if (diff > 0) {
        likeCurrentProfile();
      } else {
        skipCurrentProfile();
      }
    }
  });
}

// Button handlers
if (likeBtn) {
  likeBtn.addEventListener('click', likeCurrentProfile);
}

if (skipBtn) {
  skipBtn.addEventListener('click', skipCurrentProfile);
}

if (refreshBtn) {
  refreshBtn.addEventListener('click', refreshProfiles);
}

// Create profile panel
if (createBtn) {
  createBtn.addEventListener('click', () => {
    if (!currentUser) {
      showAuthMessage('Для создания анкеты нужно войти в аккаунт', 'error');
      authPanel.setAttribute('aria-hidden', 'false');
      return;
    }
    if (createPanel) createPanel.setAttribute('aria-hidden', 'false');
  });
}

if (createClose) {
  createClose.addEventListener('click', () => {
    if (createPanel) createPanel.setAttribute('aria-hidden', 'true');
  });
}

// Close panels with back buttons
document.querySelectorAll('.back-btn, .who-back-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    if (likedPanel) likedPanel.setAttribute('aria-hidden', 'true');
    if (whoLikedPanel) whoLikedPanel.setAttribute('aria-hidden', 'true');
  });
});

// Close profile view panel
if (profileViewClose) {
  profileViewClose.addEventListener('click', () => {
    profileViewPanel.setAttribute('aria-hidden', 'true');
    currentViewingProfile = null;
  });
}

// Auth panel
if (authBtn) {
  authBtn.addEventListener('click', () => {
    updateAuthUI();
    authPanel.setAttribute('aria-hidden', 'false');
  });
}

if (authClose) {
  authClose.addEventListener('click', () => {
    authPanel.setAttribute('aria-hidden', 'true');
  });
}

// Auth tabs
document.getElementById('login-tab').addEventListener('click', () => {
  document.getElementById('login-tab').classList.add('active');
  document.getElementById('register-tab').classList.remove('active');
  document.getElementById('login-form').style.display = 'block';
  document.getElementById('register-form').style.display = 'none';
});

document.getElementById('register-tab').addEventListener('click', () => {
  document.getElementById('register-tab').classList.add('active');
  document.getElementById('login-tab').classList.remove('active');
  document.getElementById('register-form').style.display = 'block';
  document.getElementById('login-form').style.display = 'none';
});

// Login function
document.getElementById('login-btn').addEventListener('click', async () => {
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  
  if (!email || !password) {
    showAuthMessage('Заполните все поля', 'error');
    return;
  }
  
  try {
    await loginUser(email, password);
    updateAuthUI();
    updateAuthButtonDisplay();
    updateUserStatusDisplay();
    showAuthMessage('Вход выполнен успешно!', 'success');
    setTimeout(() => {
      authPanel.setAttribute('aria-hidden', 'true');
      loadProfiles();
    }, 1000);
  } catch (error) {
    const errorMessage = getErrorMessage(error);
    showAuthMessage(errorMessage, 'error');
  }
});

// Register function
document.getElementById('register-btn').addEventListener('click', async () => {
  const email = document.getElementById('register-email').value;
  const password = document.getElementById('register-password').value;
  const confirmPassword = document.getElementById('register-confirm-password').value;
  
  if (!email || !password || !confirmPassword) {
    showAuthMessage('Заполните все поля', 'error');
    return;
  }
  
  if (password !== confirmPassword) {
    showAuthMessage('Пароли не совпадают', 'error');
    return;
  }
  
  if (password.length < 6) {
    showAuthMessage('Пароль должен быть не менее 6 символов', 'error');
    return;
  }
  
  try {
    await registerUser(email, password);
    updateAuthUI();
    updateAuthButtonDisplay();
    updateUserStatusDisplay();
    showAuthMessage('Регистрация выполнена успешно!', 'success');
    setTimeout(() => {
      authPanel.setAttribute('aria-hidden', 'true');
      loadProfiles();
    }, 1000);
  } catch (error) {
    const errorMessage = getErrorMessage(error);
    showAuthMessage(errorMessage, 'error');
  }
});

// Logout function
document.getElementById('logout-btn').addEventListener('click', () => {
  logoutUser();
  updateAuthUI();
  updateAuthButtonDisplay();
  updateUserStatusDisplay();
  showAuthMessage('Вы вышли из аккаунта', 'success');
  setTimeout(() => {
    authPanel.setAttribute('aria-hidden', 'true');
    loadProfiles();
  }, 1000);
});

// Update auth UI
function updateAuthUI() {
  const authMessage = document.getElementById('auth-message');
  authMessage.className = 'auth-message';
  authMessage.textContent = '';
  
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
    document.getElementById('login-tab').classList.add('active');
    document.getElementById('register-tab').classList.remove('active');
    
    // Clear form fields
    document.getElementById('login-email').value = '';
    document.getElementById('login-password').value = '';
    document.getElementById('register-email').value = '';
    document.getElementById('register-password').value = '';
    document.getElementById('register-confirm-password').value = '';
  }
}

// Show auth message
function showAuthMessage(message, type) {
  const authMessage = document.getElementById('auth-message');
  authMessage.textContent = message;
  authMessage.className = `auth-message ${type}`;
}

// Save profile
if (createSave) {
  createSave.addEventListener('click', async () => {
    if (!currentUser) {
      showAuthMessage('Для создания анкеты нужно войти в аккаунт', 'error');
      return;
    }
    
    const name = document.getElementById('create-name').value;
    const age = document.getElementById('create-age').value;
    const gender = document.getElementById('create-gender').value;
    const city = document.getElementById('create-city').value;
    const photo = document.getElementById('create-photo').value;
    const bio = document.getElementById('create-bio').value;
    const contact = document.getElementById('create-contact').value;
    const tags = document.getElementById('create-tags').value;
    
    if (!name || !age || !gender) {
      alert('Заполните имя, возраст и пол');
      return;
    }
    
    const profileData = {
      name,
      age: parseInt(age),
      gender,
      city,
      photo_url: photo,
      bio,
      contact_info: contact,
      tags: tags.split(',').map(t => t.trim()).filter(t => t)
    };
    
    try {
      myProfile = await createProfile(profileData);
      showNotification('Профиль создан успешно!');
      if (createPanel) createPanel.setAttribute('aria-hidden', 'true');
      
      // Clear form
      document.getElementById('create-name').value = '';
      document.getElementById('create-age').value = '';
      document.getElementById('create-gender').value = '';
      document.getElementById('create-city').value = '';
      document.getElementById('create-photo').value = '';
      document.getElementById('create-bio').value = '';
      document.getElementById('create-contact').value = '';
      document.getElementById('create-tags').value = '';
      
      // Reload profiles
      loadProfiles();
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      alert('Ошибка создания профиля: ' + errorMessage);
    }
  });
}

// Liked profiles button
const savedBtn = document.getElementById('saved-btn');
savedBtn?.addEventListener('click', async () => {
  if (!currentUser) {
    showAuthMessage('Для просмотра понравившихся нужно войти в аккаунт', 'error');
    authPanel.setAttribute('aria-hidden', 'false');
    return;
  }
  await renderLikedList();
  likedPanel?.setAttribute('aria-hidden', 'false');
});

// Who liked me button
if (whoLikedBtn) {
  whoLikedBtn.addEventListener('click', async () => {
    if (!currentUser) {
      showAuthMessage('Для просмотра лайков нужно войти в аккаунт', 'error');
      authPanel.setAttribute('aria-hidden', 'false');
      return;
    }
    await renderWhoLikedList();
    whoLikedPanel?.setAttribute('aria-hidden', 'false');
  });
}

async function renderLikedList() {
  if (!likedList) return;
  
  try {
    const likedProfiles = await getLikedProfiles();
    likedList.innerHTML = '';
    
    if (likedProfiles.length === 0) {
      likedList.innerHTML = '<div class="empty-text">Нет понравившихся профилей</div>';
      return;
    }
    
    likedProfiles.forEach(profile => {
      const item = document.createElement('div');
      item.className = 'liked-item';
      const genderEmoji = profile.gender === 'male' ? '🚮' : profile.gender === 'female' ? '🚮' : '';
      item.innerHTML = `
        <div class="profile-photo-small" style="background-image: url(${profile.photo_url || 'https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg?w=800&q=80'})"></div>
        <div class="profile-info">
          <div class="profile-name-age">${genderEmoji} ${profile.name}, ${profile.age}</div>
          <div class="profile-city">${profile.city || 'Город не указан'}</div>
        </div>
        <div class="item-actions">
          <button class="item-action-btn view-btn" data-id="${profile.id}" title="Просмотреть анкету">👁</button>
          <button class="item-action-btn unlike-btn" data-id="${profile.id}" title="Убрать лайк">✕</button>
        </div>
      `;
      likedList.appendChild(item);
    });
    
    // Add event listeners
    document.querySelectorAll('.liked-item .view-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        const profileId = parseInt(btn.getAttribute('data-id'));
        const likedProfiles = await getLikedProfiles();
        const profile = likedProfiles.find(p => p.id === profileId);
        if (profile) {
          isViewingFromLikedList = true;
          viewProfile(profile);
        }
      });
    });
    
    document.querySelectorAll('.liked-item .unlike-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        const profileId = parseInt(btn.getAttribute('data-id'));
        const likedProfiles = await getLikedProfiles();
        const profile = likedProfiles.find(p => p.id === profileId);
        if (profile) {
          await unlikeProfile(profile);
          renderLikedList();
        }
      });
    });
  } catch (error) {
    console.error('Error rendering liked list:', error);
    likedList.innerHTML = '<div class="empty-text">Ошибка загружки</div>';
  }
}

async function renderWhoLikedList() {
  if (!whoLikedList) return;
  
  try {
    const whoLiked = await getWhoLikedMe();
    const likedProfiles = await getLikedProfiles();
    
    whoLikedList.innerHTML = '';
    
    if (whoLiked.length === 0) {
      whoLikedList.innerHTML = '<div class="empty-text">Пока никто не лайкнул ваш профиль</div>';
      return;
    }
    
    whoLiked.forEach(profile => {
      const isLikedBack = likedProfiles.some(p => p.id === profile.id);
      const item = document.createElement('div');
      item.className = 'who-liked-item';
      const genderEmoji = profile.gender === 'male' ? '🚮' : profile.gender === 'female' ? '🚮' : '';
      item.innerHTML = `
        <div class="profile-photo-small" style="background-image: url(${profile.photo_url || 'https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg?w=800&q=80'})"></div>
        <div class="profile-info">
          <div class="profile-name-age">${genderEmoji} ${profile.name}, ${profile.age}</div>
          <div class="profile-city">${profile.city}</div>
        </div>
        <div class="item-actions">
          <button class="item-action-btn view-btn" data-id="${profile.id}" title="Просмотреть анкету">👁</button>
          ${isLikedBack ? 
            '<button class="item-action-btn unlike-btn" data-id="' + profile.id + '" title="Убрать лайк">✕</button>' : 
            '<button class="item-action-btn like-back-btn" data-id="' + profile.id + '" title="Лайкнуть в ответ">❤</button>'
          }
        </div>
      `;
      whoLikedList.appendChild(item);
    });
    
    // Add event listeners
    document.querySelectorAll('.who-liked-item .view-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        const profileId = parseInt(btn.getAttribute('data-id'));
        const whoLiked = await getWhoLikedMe();
        const profile = whoLiked.find(p => p.id === profileId);
        if (profile) {
          isViewingFromLikedList = false;
          viewProfile(profile);
        }
      });
    });
    
    document.querySelectorAll('.who-liked-item .like-back-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        const profileId = parseInt(btn.getAttribute('data-id'));
        const whoLiked = await getWhoLikedMe();
        const profile = whoLiked.find(p => p.id === profileId);
        if (profile) {
          await likeProfile(profile);
          renderWhoLikedList();
        }
      });
    });
    
    document.querySelectorAll('.who-liked-item .unlike-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        const profileId = parseInt(btn.getAttribute('data-id'));
        const whoLiked = await getWhoLikedMe();
        const profile = whoLiked.find(p => p.id === profileId);
        if (profile) {
          await unlikeProfile(profile);
          renderWhoLikedList();
        }
      });
    });
  } catch (error) {
    console.error('Error rendering who liked list:', error);
    whoLikedList.innerHTML = '<div class="empty-text">Ошибка загружки</div>';
  }
}

// View profile function
function viewProfile(profile) {
  currentViewingProfile = profile;
  
  document.getElementById('profile-view-photo').style.backgroundImage = `url(${profile.photo_url || 'https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg?w=800&q=80'})`;
  document.getElementById('profile-view-name').textContent = profile.name;
  document.getElementById('profile-view-age').textContent = `${profile.age} лет`;
  document.getElementById('profile-view-gender').textContent = profile.gender === 'male' ? 'Мужчина' : profile.gender === 'female' ? 'Женщина' : 'Не указан';
  document.getElementById('profile-view-city').textContent = profile.city || 'Не указан';
  document.getElementById('profile-view-bio').textContent = profile.bio || 'Не указано';
  document.getElementById('profile-view-contact').textContent = profile.contact_info || 'Не указан';
  document.getElementById('profile-view-tags').textContent = Array.isArray(profile.tags) ? profile.tags.join(', ') : 'Не указаны';
  
  // Show/hide appropriate buttons
  getLikedProfiles().then(likedProfiles => {
    const isLiked = likedProfiles.some(p => p.id === profile.id);
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

// Profile view like button
if (profileViewLikeBtn) {
  profileViewLikeBtn.addEventListener('click', async () => {
    if (currentViewingProfile) {
      if (await likeProfile(currentViewingProfile)) {
        profileViewLikeBtn.style.display = 'none';
        profileViewUnlikeBtn.style.display = 'block';
        
        if (isViewingFromLikedList) {
          await renderLikedList();
        } else {
          await renderWhoLikedList();
        }
      }
    }
  });
}

// Profile view unlike button
if (profileViewUnlikeBtn) {
  profileViewUnlikeBtn.addEventListener('click', async () => {
    if (currentViewingProfile) {
      if (await unlikeProfile(currentViewingProfile)) {
        profileViewLikeBtn.style.display = 'block';
        profileViewUnlikeBtn.style.display = 'none';
        
        if (isViewingFromLikedList) {
          await renderLikedList();
        } else {
          await renderWhoLikedList();
        }
        
        if (isViewingFromLikedList) {
          setTimeout(() => {
            profileViewPanel.setAttribute('aria-hidden', 'true');
          }, 500);
        }
      }
    }
  });
}

// Create preview
const createPreview = document.getElementById('create-preview');
const createPreviewArea = document.querySelector('.create-preview-area');

createPreview?.addEventListener('click', () => {
  const name = document.getElementById('create-name').value || "Имя";
  const age = document.getElementById('create-age').value || "Возраст";
  const gender = document.getElementById('create-gender').value;
  const city = document.getElementById('create-city').value || "Город";
  const bio = document.getElementById('create-bio').value || "О себе";
  const photo = document.getElementById('create-photo').value || "https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg?w=800&q=80";
  
  const genderEmoji = gender === 'male' ? '🚮' : gender === 'female' ? '🚮' : '';
  
  createPreviewArea.innerHTML = `
    <div class="card" style="position: relative; height: 320px; margin: 0 auto;">
      <div class="card-inner">
        <div class="card-photo" style="background-image: url(${photo})"></div>
        <div class="card-info">
          <div class="card-name-age">${genderEmoji} ${name}, ${age}</div>
          <div class="card-city">${city}</div>
          <div class="card-bio">${bio}</div>
        </div>
      </div>
    </div>
    <button onclick="document.querySelector('.create-preview-area').setAttribute('aria-hidden', 'true')" style="margin-top: 12px; width: 100%; padding: 10px;">Закрыть предпросмотр</button>
  `;
  createPreviewArea.setAttribute('aria-hidden', 'false');
});

// Logo click handler
const logoRow = document.querySelector('.logo-row');
logoRow?.addEventListener('click', () => {
  const url = prompt('Введите URL логотипа:', 'https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg?w=800&q=80');
  if (url) {
    document.getElementById('logo-img').src = url;
  }
});

// Filter change handlers
if (cityFilter) {
  cityFilter.addEventListener('change', loadProfiles);
}

if (genderFilter) {
  genderFilter.addEventListener('change', loadProfiles);
}

// Apply theme on load
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

// Theme toggle
if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    darkMode = !darkMode;
    localStorage.setItem('darkMode', darkMode ? '1' : '0');
    applyTheme();
  });
}

// Initialize app
window.addEventListener('DOMContentLoaded', async () => {
  // Check if user is logged in
  if (authToken) {
    try {
      console.log('🔍 Checking if user is still logged in...');
      console.log('Token preview:', authToken.substring(0, 20) + '...');
      currentUser = await apiRequest('/users/me');
      console.log('✅ User is logged in:', currentUser.email);
    } catch (error) {
      console.error('⚠️  Error fetching user:', error);
      authToken = null;
      currentUser = null;
      localStorage.removeItem('authToken');
    }
  }
  
  updateAuthUI();
  updateAuthButtonDisplay();
  updateUserStatusDisplay();
  await loadProfiles();
});