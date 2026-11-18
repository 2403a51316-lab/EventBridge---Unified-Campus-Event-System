/**
 * Smart Campus Event Management System
 * Shared Authentication, Role Guards, and Dynamic Navbar Helper
 */

const AUTH_KEYS = {
  TOKEN: 'campus_token',
  USER: 'campus_user'
};

/**
 * Save user authentication payload to localStorage
 * @param {string} token 
 * @param {object} user 
 */
function saveAuth(token, user) {
  localStorage.setItem(AUTH_KEYS.TOKEN, token);
  localStorage.setItem(AUTH_KEYS.USER, JSON.stringify(user));
}

/**
 * Get stored JWT token
 * @returns {string|null}
 */
function getToken() {
  return localStorage.getItem(AUTH_KEYS.TOKEN);
}

/**
 * Get logged-in user object
 * @returns {object|null}
 */
function getUser() {
  const userJson = localStorage.getItem(AUTH_KEYS.USER);
  if (!userJson) return null;
  try {
    return JSON.parse(userJson);
  } catch (e) {
    return null;
  }
}

/**
 * Update locally cached user object
 * @param {object} updatedFields 
 */
function updateUserCache(updatedFields) {
  const current = getUser();
  if (current) {
    const updated = { ...current, ...updatedFields };
    localStorage.setItem(AUTH_KEYS.USER, JSON.stringify(updated));
  }
}

/**
 * Check if a session exists
 * @returns {boolean}
 */
function isLoggedIn() {
  return !!getToken() && !!getUser();
}

/**
 * Check if the logged-in user holds a specific role
 * @param {string|string[]} roles 
 * @returns {boolean}
 */
function hasRole(roles) {
  const user = getUser();
  if (!user) return false;
  const roleList = Array.isArray(roles) ? roles : [roles];
  return roleList.includes(user.role);
}

/**
 * Get target dashboard URL for a given role
 * @param {string} role 
 * @returns {string}
 */
function getDashboardUrl(role) {
  switch (role) {
    case 'admin':
      return 'admin-dashboard.html';
    case 'organizer':
      return 'organizer-dashboard.html';
    case 'student':
    default:
      return 'student-dashboard.html';
  }
}

/**
 * End current session and redirect to login
 */
function logout() {
  localStorage.removeItem(AUTH_KEYS.TOKEN);
  localStorage.removeItem(AUTH_KEYS.USER);
  showToast('Logged out successfully', 'info');
  setTimeout(() => {
    window.location.href = 'login.html';
  }, 400);
}

/**
 * Route protection guard for client-side pages
 * Enforces role-based isolation and prevents manual URL tampering
 * @param {string[]} allowedRoles - Roles allowed to view this page (e.g. ['admin'], ['organizer'])
 */
function requireAuth(allowedRoles = []) {
  if (!isLoggedIn()) {
    showToast('Please log in to access this page.', 'warning');
    setTimeout(() => {
      window.location.href = 'login.html';
    }, 500);
    return false;
  }

  const user = getUser();
  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    const roleCapitalized = user.role.charAt(0).toUpperCase() + user.role.slice(1);
    showToast(`Access Restricted: This dashboard is reserved for ${allowedRoles.join(' or ')} accounts. Redirecting to your ${roleCapitalized} Dashboard...`, 'danger');
    setTimeout(() => {
      window.location.href = getDashboardUrl(user.role);
    }, 1200);
    return false;
  }

  return true;
}

/**
 * Renders dynamic navbar based on user session and role.
 * Injects directly into #mainNavbar element on all frontend pages.
 */
function renderNavbar() {
  const navContainer = document.getElementById('mainNavbar');
  if (!navContainer) return;

  const user = getUser();
  const currentPath = window.location.pathname;
  const isCurrent = (page) => currentPath.endsWith(page) ? 'active' : '';

  let roleLinks = '';
  let authActions = '';

  if (user) {
    const roleBadgeClass = {
      admin: 'bg-danger text-white',
      organizer: 'bg-warning text-dark',
      student: 'bg-success text-white'
    }[user.role] || 'bg-secondary text-white';

    // Student Links
    if (user.role === 'student') {
      roleLinks = `
        <li class="nav-item">
          <a class="nav-link ${isCurrent('student-dashboard.html')}" href="student-dashboard.html">
            <i class="bi bi-speedometer2 me-1"></i> Student Dashboard
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${isCurrent('events.html')}" href="events.html">
            <i class="bi bi-compass me-1"></i> Browse Events
          </a>
        </li>
      `;
    }

    // Organizer Links
    if (user.role === 'organizer') {
      roleLinks = `
        <li class="nav-item">
          <a class="nav-link ${isCurrent('organizer-dashboard.html')}" href="organizer-dashboard.html">
            <i class="bi bi-speedometer2 me-1"></i> Organizer Dashboard
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${isCurrent('events.html')}" href="events.html">
            <i class="bi bi-globe me-1"></i> Public Catalog
          </a>
        </li>
      `;
    }

    // Admin Links
    if (user.role === 'admin') {
      roleLinks = `
        <li class="nav-item">
          <a class="nav-link ${isCurrent('admin-dashboard.html')}" href="admin-dashboard.html">
            <i class="bi bi-shield-lock me-1"></i> Admin Console
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link ${isCurrent('events.html')}" href="events.html">
            <i class="bi bi-globe me-1"></i> Campus Events
          </a>
        </li>
      `;
    }

    authActions = `
      <div class="d-flex align-items-center gap-3 ms-lg-3 mt-3 mt-lg-0">
        <div class="text-white d-flex align-items-center gap-2">
          <div class="stat-icon bg-white bg-opacity-10 text-info" style="width: 38px; height: 38px; font-size: 1.1rem; border-radius: 50%;">
            <i class="bi bi-person-fill"></i>
          </div>
          <div>
            <div class="fw-semibold text-truncate" style="max-width: 140px;">${user.name}</div>
            <span class="badge ${roleBadgeClass} user-badge">${user.role}</span>
          </div>
        </div>
        <button class="btn btn-outline-light btn-sm d-flex align-items-center gap-1" onclick="logout()">
          <i class="bi bi-box-arrow-right"></i> Logout
        </button>
      </div>
    `;
  } else {
    // Logged Out Visitor
    roleLinks = `
      <li class="nav-item">
        <a class="nav-link ${isCurrent('events.html')}" href="events.html">
          <i class="bi bi-calendar3 me-1"></i> Public Events
        </a>
      </li>
    `;

    authActions = `
      <div class="d-flex align-items-center gap-2 ms-lg-3 mt-3 mt-lg-0">
        <a href="login.html" class="btn btn-outline-light btn-sm px-3">
          <i class="bi bi-box-arrow-in-right me-1"></i> Sign In
        </a>
        <a href="register.html" class="btn btn-warning btn-sm px-3 fw-semibold">
          <i class="bi bi-person-plus me-1"></i> Register
        </a>
      </div>
    `;
  }

  navContainer.className = 'navbar navbar-expand-lg navbar-dark navbar-custom sticky-top';
  navContainer.innerHTML = `
    <div class="container-fluid px-lg-4">
      <a class="navbar-brand" href="index.html">
        <i class="bi bi-mortarboard-fill text-warning"></i>
        <span>Smart<span class="text-info">Campus</span> Events</span>
      </a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarContent"
        aria-controls="navbarContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <a class="nav-link ${isCurrent('index.html') || currentPath === '/' ? 'active' : ''}" href="index.html">
              <i class="bi bi-house-door me-1"></i> Home
            </a>
          </li>
          ${roleLinks}
        </ul>
        ${authActions}
      </div>
    </div>
  `;
}

// Auto-render navbar when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  renderNavbar();
});
