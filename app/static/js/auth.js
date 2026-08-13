(function () {
  const apiBase = '/api/auth';

  function togglePasswordVisibility(event) {
    const targetId = event.currentTarget.dataset.target;
    const input = document.getElementById(targetId);
    if (!input) return;
    input.type = input.type === 'password' ? 'text' : 'password';
    event.currentTarget.querySelector('i').className = input.type === 'password' ? 'bi bi-eye' : 'bi bi-eye-slash';
  }

  function showAlert(message, type = 'danger') {
    const alertBox = document.getElementById('authAlert');
    if (!alertBox) return;
    alertBox.className = `alert alert-${type}`;
    alertBox.textContent = message;
    alertBox.classList.remove('d-none');
  }

  function setLoading(form, loading) {
    const button = form.querySelector('button[type="submit"]');
    const spinner = button?.querySelector('.spinner-border');
    const label = button?.querySelector('.btn-label');
    if (!button || !spinner || !label) return;
    button.disabled = loading;
    spinner.classList.toggle('d-none', !loading);
    label.textContent = loading ? 'Đang xử lý...' : button.closest('#loginForm') ? 'Đăng nhập' : 'Tạo tài khoản';
  }

  async function requestJson(url, method, body) {
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.message || 'Đã xảy ra lỗi');
    }
    return data;
  }

  async function handleLogin(event) {
    event.preventDefault();
    const form = event.currentTarget;
    setLoading(form, true);
    try {
      const payload = Object.fromEntries(new FormData(form).entries());
      const data = await requestJson(`${apiBase}/login`, 'POST', payload);
      localStorage.setItem('access_token', data.data.access_token);
      localStorage.setItem('refresh_token', data.data.refresh_token);
      window.location.href = '/itineraries';
    } catch (error) {
      showAlert(error.message);
    } finally {
      setLoading(form, false);
    }
  }

  async function handleRegister(event) {
    event.preventDefault();
    const form = event.currentTarget;
    setLoading(form, true);
    try {
      const payload = Object.fromEntries(new FormData(form).entries());
      if (payload.password !== payload.confirm_password) {
        throw new Error('Mật khẩu xác nhận không khớp');
      }
      delete payload.confirm_password;
      const data = await requestJson(`${apiBase}/register`, 'POST', payload);
      localStorage.setItem('access_token', data.data.access_token);
      localStorage.setItem('refresh_token', data.data.refresh_token);
      window.location.href = '/itineraries/create';
    } catch (error) {
      showAlert(error.message);
    } finally {
      setLoading(form, false);
    }
  }

  document.querySelectorAll('.toggle-password').forEach((button) => button.addEventListener('click', togglePasswordVisibility));
  document.getElementById('loginForm')?.addEventListener('submit', handleLogin);
  document.getElementById('registerForm')?.addEventListener('submit', handleRegister);
})();
