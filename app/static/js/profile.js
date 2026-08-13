(function () {
  const profileForm = document.getElementById('profileForm');
  const passwordForm = document.getElementById('passwordForm');
  const profileAlert = document.getElementById('profileAlert');

  function tokenHeaders() {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  function showAlert(message, type = 'danger') {
    if (!profileAlert) return;
    profileAlert.className = `alert alert-${type} rounded-3 animate__animated animate__fadeIn`;
    profileAlert.textContent = message;
    profileAlert.classList.remove('d-none');
  }

  function hideAlert() {
    if (profileAlert) profileAlert.classList.add('d-none');
  }

  function getErrorMessage(result, fallback) {
    if (Array.isArray(result.details)) {
      const messages = result.details
        .map((item) => item.msg || item.message)
        .filter(Boolean);
      if (messages.length) return messages.join('; ');
    }
    return result.detail || result.message || fallback;
  }

  async function loadUserProfile() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      window.location.href = '/auth/login';
      return;
    }

    try {
      const response = await fetch('/api/users/me', {
        headers: tokenHeaders(),
      });
      if (!response.ok) throw new Error('Khong the tai thong tin ca nhan');

      const user = await response.json();

      document.getElementById('displayFullName').textContent = user.full_name || 'Nguoi dung';
      document.getElementById('displayEmail').textContent = user.email || '';

      document.getElementById('inputFullName').value = user.full_name || '';
      document.getElementById('inputEmail').value = user.email || '';
      document.getElementById('inputPhone').value = user.phone || '';
      document.getElementById('inputAddress').value = user.address || '';

      document.getElementById('displayPhone').textContent = user.phone || 'Chua cap nhat';
      document.getElementById('displayAddress').textContent = user.address || 'Chua cap nhat';
      document.getElementById('displayCreatedAt').textContent = user.created_at
        ? new Date(user.created_at).toLocaleDateString('vi-VN')
        : 'Chua cap nhat';
    } catch (error) {
      showAlert(error.message, 'danger');
    }
  }

  if (profileForm) {
    profileForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideAlert();

      const formData = new FormData(profileForm);
      const payload = {
        full_name: formData.get('full_name'),
        phone: formData.get('phone') || null,
        address: formData.get('address') || null,
        avatar_url: null,
      };

      try {
        const response = await fetch('/api/users/me', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            ...tokenHeaders(),
          },
          body: JSON.stringify(payload),
        });

        const result = await response.json();
        if (!response.ok) {
          throw new Error(getErrorMessage(result, 'Cap nhat that bai'));
        }

        showAlert('Cap nhat thong tin ca nhan thanh cong!', 'success');
        loadUserProfile();
      } catch (error) {
        showAlert(error.message, 'danger');
      }
    });
  }

  if (passwordForm) {
    passwordForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideAlert();

      const formData = new FormData(passwordForm);
      const oldPassword = String(formData.get('old_password') || '');
      const newPassword = String(formData.get('new_password') || '');
      const confirmPassword = String(formData.get('confirm_password') || '');

      if (!oldPassword) {
        showAlert('Vui long nhap mat khau hien tai', 'warning');
        return;
      }

      if (newPassword.length < 8) {
        showAlert('Mat khau moi phai co it nhat 8 ky tu', 'warning');
        return;
      }

      if (newPassword !== confirmPassword) {
        showAlert('Mat khau moi va xac nhan mat khau khong khop!', 'warning');
        return;
      }

      try {
        const response = await fetch('/api/users/me/password', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            ...tokenHeaders(),
          },
          body: JSON.stringify({
            current_password: oldPassword,
            old_password: oldPassword,
            new_password: newPassword,
          }),
        });

        const result = await response.json();
        if (!response.ok) {
          throw new Error(getErrorMessage(result, 'Doi mat khau that bai'));
        }

        showAlert('Doi mat khau thanh cong!', 'success');
        passwordForm.reset();
      } catch (error) {
        showAlert(error.message, 'danger');
      }
    });
  }

  document.addEventListener('DOMContentLoaded', loadUserProfile);
})();
