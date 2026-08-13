(function () {
  document.addEventListener('DOMContentLoaded', initItineraryForm);

  function initItineraryForm() {
    const form = document.getElementById('itineraryForm');
    if (!form) return;

    const alertBox = document.getElementById('itineraryAlert');
    const totalBudget = document.getElementById('totalBudget');

    const rowContainers = {
      members: document.getElementById('membersRows'),
      schedule: document.getElementById('scheduleRows'),
      places: document.getElementById('placesRows'),
      tasks: document.getElementById('tasksRows'),
    };

    const rowTemplates = {
      members: () => `
        <div class="row g-2 align-items-end dynamic-row">
          <div class="col-md-5"><label class="form-label small text-muted">Họ tên</label><input class="form-control rounded-3" data-field="name" placeholder="Nguyễn Văn A"></div>
          <div class="col-md-3"><label class="form-label small text-muted">Vai trò</label><input class="form-control rounded-3" data-field="role" placeholder="Bạn bè / Gia đình"></div>
          <div class="col-md-3"><label class="form-label small text-muted">Số điện thoại</label><input class="form-control rounded-3" data-field="phone" placeholder="090..."></div>
          <div class="col-md-1 d-grid"><button class="btn btn-light border rounded-3" type="button" data-remove-row><i class="bi bi-trash"></i></button></div>
        </div>
      `,
      schedule: () => `
        <div class="row g-2 align-items-end dynamic-row">
          <div class="col-md-2"><label class="form-label small text-muted">Ngày</label><input class="form-control rounded-3" type="number" min="1" data-field="day" placeholder="1"></div>
          <div class="col-md-2"><label class="form-label small text-muted">Giờ</label><input class="form-control rounded-3" data-field="time" placeholder="08:00 - 10:00"></div>
          <div class="col-md-3"><label class="form-label small text-muted">Hoạt động</label><input class="form-control rounded-3" data-field="activity" placeholder="Tham quan"></div>
          <div class="col-md-4"><label class="form-label small text-muted">Ghi chú</label><input class="form-control rounded-3" data-field="note" placeholder="Địa chỉ, lưu ý di chuyển"></div>
          <div class="col-md-1 d-grid"><button class="btn btn-light border rounded-3" type="button" data-remove-row><i class="bi bi-trash"></i></button></div>
        </div>
      `,
      places: () => `
        <div class="row g-2 align-items-end dynamic-row">
          <div class="col-md-3"><label class="form-label small text-muted">Loại</label><select class="form-select rounded-3" data-field="type"><option>Địa điểm tham quan</option><option>Nhà hàng</option><option>Khách sạn</option></select></div>
          <div class="col-md-4"><label class="form-label small text-muted">Tên</label><input class="form-control rounded-3" data-field="name" placeholder="Bà Nà Hills / Nhà hàng..."></div>
          <div class="col-md-4"><label class="form-label small text-muted">Địa chỉ / ghi chú</label><input class="form-control rounded-3" data-field="note" placeholder="Khu vực, giá dự kiến, giờ mở cửa"></div>
          <div class="col-md-1 d-grid"><button class="btn btn-light border rounded-3" type="button" data-remove-row><i class="bi bi-trash"></i></button></div>
        </div>
      `,
      tasks: () => `
        <div class="row g-2 align-items-end dynamic-row">
          <div class="col-md-5"><label class="form-label small text-muted">Công việc</label><input class="form-control rounded-3" data-field="task" placeholder="Đặt phòng / chuẩn bị giấy tờ"></div>
          <div class="col-md-3"><label class="form-label small text-muted">Người phụ trách</label><input class="form-control rounded-3" data-field="owner" placeholder="Tên thành viên"></div>
          <div class="col-md-3"><label class="form-label small text-muted">Trạng thái</label><select class="form-select rounded-3" data-field="status"><option>Cần làm</option><option>Đang làm</option><option>Đã xong</option></select></div>
          <div class="col-md-1 d-grid"><button class="btn btn-light border rounded-3" type="button" data-remove-row><i class="bi bi-trash"></i></button></div>
        </div>
      `,
    };

    function showAlert(message, type = 'danger') {
      if (!alertBox) return;
      alertBox.className = `alert alert-${type} rounded-3`;
      alertBox.textContent = message;
      alertBox.classList.remove('d-none');
    }

    function setSubmitLoading(loading) {
      const button = form.querySelector('button[type="submit"]');
      const spinner = button?.querySelector('.spinner-border');
      const label = button?.querySelector('.btn-label');
      if (!button || !spinner || !label) return;
      button.disabled = loading;
      spinner.classList.toggle('d-none', !loading);
      label.innerHTML = loading ? 'Đang lưu...' : '<i class="bi bi-save me-2"></i>Lưu chuyến đi';
    }

    function asNumber(value) {
      return Number.parseFloat(String(value || '0').replace(/[^\d.]/g, '')) || 0;
    }

    function updateTotalBudget() {
      const total = Array.from(document.querySelectorAll('.cost-input')).reduce((sum, input) => sum + asNumber(input.value), 0);
      if (totalBudget) totalBudget.value = String(total || 1);
    }

    function collectRows(type) {
      return Array.from(rowContainers[type]?.querySelectorAll('.dynamic-row') || [])
        .map((row) => {
          const item = {};
          row.querySelectorAll('[data-field]').forEach((field) => {
            item[field.dataset.field] = field.value.trim();
          });
          return item;
        })
        .filter((item) => Object.values(item).some(Boolean));
    }

    function buildPlanNotes(formData) {
      const costs = {
        'Ăn uống': formData.get('food_cost'),
        'Di chuyển': formData.get('transport_cost'),
        'Lưu trú': formData.get('stay_cost'),
        'Vé tham quan': formData.get('ticket_cost'),
      };
      return [
        `Trạng thái: ${formData.get('plan_status') || 'Dự định'}`,
        `Thành viên: ${JSON.stringify(collectRows('members'))}`,
        `Lịch trình: ${JSON.stringify(collectRows('schedule'))}`,
        `Địa điểm/Nhà hàng/Khách sạn: ${JSON.stringify(collectRows('places'))}`,
        `Checklist chuẩn bị: ${JSON.stringify(collectRows('tasks'))}`,
        `Chi phí dự kiến: ${JSON.stringify(costs)}`,
        `Ghi chú: ${formData.get('plan_note') || ''}`,
      ].join('\n');
    }

    async function requestJson(url, method, body) {
      const token = localStorage.getItem('access_token');
      if (!token) {
        window.location.href = '/auth/login';
        throw new Error('Vui lòng đăng nhập trước khi lưu chuyến đi');
      }
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(body),
      });
      const data = await response.json();
      if (!response.ok) {
        const detailMessage = Array.isArray(data.details)
          ? data.details.map((item) => item.msg || item.message).filter(Boolean).join('; ')
          : '';
        throw new Error(data.message || detailMessage || data.detail || 'Không thể xử lý yêu cầu');
      }
      return data;
    }

    function collectTripPayload() {
      updateTotalBudget();
      const formData = new FormData(form);
      const members = collectRows('members');
      return {
        trip_title: formData.get('trip_title')?.toString().trim() || '',
        origin: formData.get('origin')?.toString().trim() || '',
        destination: formData.get('destination')?.toString().trim() || '',
        start_date: formData.get('start_date'),
        number_of_days: Number.parseInt(formData.get('number_of_days') || '1', 10),
        adults: Math.max(members.length, 1),
        children: 0,
        budget: Math.max(asNumber(totalBudget?.value), 1),
        currency: formData.get('currency')?.toString().trim() || 'VND',
        plan_status: formData.get('plan_status')?.toString().trim() || 'DRAFT',
        destination_features: collectRows('places').map((place) => `${place.type}: ${place.name}`).filter(Boolean),
        travel_styles: [],
        interests: [],
        transportation_preference: '',
        accommodation_preference: '',
        dietary_requirements: [],
        travel_pace: '',
        must_visit_places: collectRows('places').map((place) => place.name).filter(Boolean),
        excluded_activities: [],
        additional_notes: buildPlanNotes(formData),
        strict_budget: false,
      };
    }

    async function handleSubmit(event) {
      event.preventDefault();
      setSubmitLoading(true);
      try {
        const data = await requestJson('/api/itineraries', 'POST', collectTripPayload());
        showAlert('Đã lưu chuyến đi mới.', 'success');
        window.location.href = `/itineraries/${data.data.id}`;
      } catch (error) {
        showAlert(error.message);
      } finally {
        setSubmitLoading(false);
      }
    }

    function addRow(type) {
      const container = rowContainers[type];
      if (!container || !rowTemplates[type]) return;
      container.insertAdjacentHTML('beforeend', rowTemplates[type]());
      container.lastElementChild?.querySelector('input, select')?.focus();
    }

    function resetDynamicRows() {
      Object.values(rowContainers).forEach((container) => {
        if (container) container.innerHTML = '';
      });
      ['members', 'schedule', 'places', 'tasks'].forEach(addRow);
    }

    document.querySelectorAll('[data-add-row]').forEach((button) => {
      button.addEventListener('click', () => addRow(button.dataset.addRow));
    });

    document.addEventListener('click', (event) => {
      const removeButton = event.target.closest('[data-remove-row]');
      if (removeButton) removeButton.closest('.dynamic-row')?.remove();
    });

    document.querySelectorAll('.cost-input').forEach((input) => input.addEventListener('input', updateTotalBudget));
    form.addEventListener('submit', handleSubmit);
    form.addEventListener('reset', () => {
      setTimeout(() => {
        resetDynamicRows();
        updateTotalBudget();
      }, 0);
    });

    resetDynamicRows();
    updateTotalBudget();
  }
})();
