const API_BASE = '/api';

async function apiRequest(endpoint, options = {}) {
  const url = endpoint.startsWith('http')
    ? endpoint
    : `${API_BASE}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  const token = localStorage.getItem('campus_token');
  if (token) headers.Authorization = `Bearer ${token}`;

  const fetchConfig = { ...options, headers };
  if (fetchConfig.body && typeof fetchConfig.body === 'object' && !(fetchConfig.body instanceof FormData)) {
    fetchConfig.body = JSON.stringify(fetchConfig.body);
  }

  try {
    const response = await fetch(url, fetchConfig);
    let result;
    try {
      result = await response.json();
    } catch {
      result = {
        success: response.ok,
        message: response.statusText || 'Unable to parse server response',
        data: null
      };
    }

    if (response.status === 401 && token && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/register')) {
      localStorage.removeItem('campus_token');
      localStorage.removeItem('campus_user');
      if (typeof showToast === 'function') showToast('Your session has expired. Please log in again.', 'warning');
    }
    return result;
  } catch (error) {
    console.error('[API Request Failure]:', error);
    return {
      success: false,
      message: 'Network connection error. Please ensure the server is running.',
      data: null
    };
  }
}

function showToast(message, type = 'info') {
  const region = document.getElementById('toastRegion') || document.body;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  region.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

function setLoading(isLoading, message = 'Loading campus data...') {
  let overlay = document.getElementById('loadingOverlay');
  if (!overlay && isLoading) {
    overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.className = 'loading-overlay active';
    overlay.innerHTML = '<span class="spinner"></span><strong></strong>';
    document.body.appendChild(overlay);
  }
  if (!overlay) return;
  overlay.classList.toggle('active', isLoading);
  const label = overlay.querySelector('strong');
  if (label) label.textContent = message;
}

function formatDateTime(dateString) {
  if (!dateString) return 'TBA';
  return new Date(dateString).toLocaleString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: 'numeric', minute: '2-digit'
  });
}

function formatDate(dateString) {
  if (!dateString) return 'TBA';
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric'
  });
}
