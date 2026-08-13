(function () {
  const listContainer = document.getElementById('itineraryList');
  const pagination = document.getElementById('pagination');
  const listState = document.getElementById('listState');
  const timelineContainer = document.getElementById('timelineContainer');
  const timelineState = document.getElementById('timelineState');
  const detailHeader = document.getElementById('detailHeader');
  const searchInput = document.getElementById('searchInput');
  const statusTabs = document.getElementById('statusTabs');
  const refreshListBtn = document.getElementById('refreshListBtn');

  const itineraryId = window.ITINERARY_ID;
  const pageSize = 12;
  let currentPage = 1;
  let currentStatus = '';

  const destinationImages = {
    'đà nẵng': 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?auto=format&fit=crop&w=700&q=80',
    'hội an': 'https://images.unsplash.com/photo-1552554942-126ac05b630b?auto=format&fit=crop&w=700&q=80',
    'đà lạt': 'https://images.unsplash.com/photo-1506461883276-594a12b11cf3?auto=format&fit=crop&w=700&q=80',
    'phú quốc': 'https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=700&q=80',
    'nha trang': 'https://images.unsplash.com/photo-1570784423858-69aa4ef124c6?auto=format&fit=crop&w=700&q=80',
    'hà nội': 'https://images.unsplash.com/photo-1509030450996-939a7307a05a?auto=format&fit=crop&w=700&q=80',
    'hạ long': 'https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=700&q=80',
    'sa pa': 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?auto=format&fit=crop&w=700&q=80',
  };

  const statusMeta = {
    DRAFT: { text: 'Dự định', className: 'bg-primary-subtle text-primary' },
    GENERATING: { text: 'Đang diễn ra', className: 'bg-warning-subtle text-warning-emphasis' },
    COMPLETED: { text: 'Đã hoàn thành', className: 'bg-success-subtle text-success' },
    FAILED: { text: 'Lỗi', className: 'bg-danger-subtle text-danger' },
    CANCELLED: { text: 'Đã hủy', className: 'bg-secondary-subtle text-secondary' },
  };

  function getDestImage(destinationStr) {
    if (!destinationStr) return 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=700&q=80';
    const lower = destinationStr.toLowerCase();
    for (const [key, url] of Object.entries(destinationImages)) {
      if (lower.includes(key)) return url;
    }
    return 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=700&q=80';
  }

  function tokenHeaders() {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async function fetchJson(url, options = {}) {
    const response = await fetch(url, { ...options, headers: { ...tokenHeaders(), ...(options.headers || {}) } });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (response.status === 401) window.location.href = '/auth/login';
      const detailMessage = Array.isArray(data.details)
        ? data.details.map((item) => item.msg || item.message).filter(Boolean).join('; ')
        : '';
      throw new Error(data.message || detailMessage || data.detail || 'Không thể tải dữ liệu');
    }
    return data;
  }

  function escapeHtml(value) {
    return String(value ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');
  }

  function formatMoney(value, currency = 'VND') {
    return `${Number(value || 0).toLocaleString('vi-VN')} ${currency || 'VND'}`;
  }

  function renderEmpty(target, message) {
    if (!target) return;
    target.innerHTML = `
      <div class="col-12">
        <div class="text-center py-5 text-muted bg-white rounded-4 border p-4">
          <div class="display-6 mb-2"><i class="bi bi-map"></i></div>
          <div class="fw-semibold text-dark mb-1">${escapeHtml(message)}</div>
          <a class="btn btn-primary-gradient text-white rounded-3 mt-3" href="/itineraries/create">Tạo chuyến đi mới</a>
        </div>
      </div>`;
  }

  function updateStats(items) {
    const totalEl = document.querySelector('[data-stat="total"]');
    const activeEl = document.querySelector('[data-stat="active"]');
    const budgetEl = document.querySelector('[data-stat="budget"]');
    if (!totalEl || !activeEl || !budgetEl) return;
    totalEl.textContent = String(items.length);
    activeEl.textContent = String(items.filter((item) => item.status !== 'COMPLETED' && item.status !== 'CANCELLED').length);
    const totalBudget = items.reduce((sum, item) => sum + Number(item.total_budget || 0), 0);
    budgetEl.textContent = formatMoney(totalBudget, items[0]?.currency || 'VND');
  }

  function renderList(items) {
    if (!listContainer) return;
    updateStats(items);
    if (!items.length) {
      renderEmpty(listContainer, 'Chưa có chuyến đi nào.');
      return;
    }

    listContainer.innerHTML = items
      .map((item) => {
        const meta = statusMeta[item.status] || { text: item.status || 'Dự định', className: 'bg-light text-muted' };
        const nights = Math.max(Number(item.number_of_days || 1) - 1, 0);
        return `
          <div class="col-md-6 col-xl-4">
            <div class="card border-0 shadow-sm rounded-4 overflow-hidden h-100 bg-white">
              <a href="/itineraries/${item.id}" class="d-block text-decoration-none">
                <img src="${getDestImage(item.destination)}" alt="${escapeHtml(item.destination)}" class="w-100" style="height: 170px; object-fit: cover;">
              </a>
              <div class="p-3 d-flex flex-column h-100">
                <div class="d-flex justify-content-between align-items-start gap-2 mb-2">
                  <div>
                    <a href="/itineraries/${item.id}" class="h5 fw-bold text-dark text-decoration-none mb-1 d-block">${escapeHtml(item.trip_title || item.destination)}</a>
                    <div class="small text-muted"><i class="bi bi-geo-alt me-1"></i>${escapeHtml(item.destination)}</div>
                  </div>
                  <span class="badge ${meta.className} rounded-pill px-2 py-1">${meta.text}</span>
                </div>

                <div class="row g-2 small text-muted my-2">
                  <div class="col-6"><i class="bi bi-calendar-event me-1"></i>${escapeHtml(item.start_date)} - ${escapeHtml(item.end_date)}</div>
                  <div class="col-6"><i class="bi bi-moon-stars me-1"></i>${item.number_of_days} ngày ${nights} đêm</div>
                  <div class="col-6"><i class="bi bi-people me-1"></i>${Number(item.adults || 0) + Number(item.children || 0)} người</div>
                  <div class="col-6"><i class="bi bi-wallet2 me-1"></i>${formatMoney(item.total_budget, item.currency)}</div>
                </div>

                <div class="d-flex gap-2 mt-auto pt-2">
                  <a href="/itineraries/${item.id}" class="btn btn-light border btn-sm rounded-3 flex-grow-1"><i class="bi bi-eye me-1"></i>Xem</a>
                  <a href="/api/itineraries/${item.id}/pdf" target="_blank" class="btn btn-light border btn-sm rounded-3"><i class="bi bi-file-earmark-pdf"></i></a>
                  <button class="btn btn-light border btn-sm rounded-3 text-danger delete-btn" type="button" data-id="${item.id}"><i class="bi bi-trash"></i></button>
                </div>
              </div>
            </div>
          </div>`;
      })
      .join('');

    listContainer.querySelectorAll('.delete-btn').forEach((btn) => {
      btn.addEventListener('click', async (event) => {
        const id = event.currentTarget.dataset.id;
        if (!confirm('Bạn có chắc chắn muốn xóa chuyến đi này không?')) return;
        try {
          await fetchJson(`/api/itineraries/${id}`, { method: 'DELETE' });
          loadList();
        } catch (error) {
          alert(error.message);
        }
      });
    });
  }

  function renderPagination(totalCount) {
    if (!pagination) return;
    const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));
    pagination.innerHTML = '';
    if (totalPages <= 1) return;
    for (let page = 1; page <= totalPages; page += 1) {
      pagination.insertAdjacentHTML('beforeend', `<li class="page-item ${page === currentPage ? 'active' : ''}"><button class="page-link rounded-2 mx-1" data-page="${page}">${page}</button></li>`);
    }
    pagination.querySelectorAll('button[data-page]').forEach((button) => {
      button.addEventListener('click', () => {
        currentPage = Number(button.dataset.page);
        loadList();
      });
    });
  }

  function parsePlanNotes(text) {
    const sections = {
      status: '',
      members: [],
      schedule: [],
      places: [],
      tasks: [],
      costs: {},
      note: '',
    };
    String(text || '').split('\n').forEach((line) => {
      const [label, ...rest] = line.split(':');
      const value = rest.join(':').trim();
      if (!label) return;
      try {
        if (label.startsWith('Trạng thái')) sections.status = value;
        if (label.startsWith('Thành viên')) sections.members = JSON.parse(value || '[]');
        if (label.startsWith('Lịch trình')) sections.schedule = JSON.parse(value || '[]');
        if (label.startsWith('Địa điểm')) sections.places = JSON.parse(value || '[]');
        if (label.startsWith('Checklist')) sections.tasks = JSON.parse(value || '[]');
        if (label.startsWith('Chi phí')) sections.costs = JSON.parse(value || '{}');
        if (label.startsWith('Ghi chú')) sections.note = value;
      } catch (_) {
        // Keep the page usable even if an older note format cannot be parsed.
      }
    });
    return sections;
  }

  function renderManualTimeline(plan) {
    if (!timelineContainer) return;
    if (!plan.schedule.length) {
      timelineContainer.innerHTML = `
        <div class="card border-0 shadow-sm rounded-4 p-4 bg-white text-muted">
          Chưa có lịch trình theo ngày và khung giờ.
        </div>`;
      return;
    }

    const grouped = plan.schedule.reduce((groups, item) => {
      const day = item.day || '1';
      groups[day] = groups[day] || [];
      groups[day].push(item);
      return groups;
    }, {});

    timelineContainer.innerHTML = `
      <div class="timeline-wrapper">
        ${Object.entries(grouped).map(([day, items]) => `
          <div class="timeline-day-block">
            <div class="timeline-day-node"></div>
            <div class="d-flex align-items-center gap-2 mb-3">
              <span class="timeline-day-title">Ngày ${escapeHtml(day)}</span>
            </div>
            <div class="vstack gap-3">
              ${items.map((item) => `
                <div class="timeline-activity-card">
                  <div class="d-flex align-items-start gap-3">
                    <span class="activity-time-badge fs-6">${escapeHtml(item.time || '--:--')}</span>
                    <div>
                      <h6 class="fw-bold text-dark mb-1">${escapeHtml(item.activity || 'Hoạt động')}</h6>
                      <p class="text-muted small mb-0">${escapeHtml(item.note || '')}</p>
                    </div>
                  </div>
                </div>`).join('')}
            </div>
          </div>`).join('')}
      </div>`;
  }

  function renderOverview(detail, timeline, plan) {
    const overviewEl = document.getElementById('overviewContent');
    if (!overviewEl) return;
    const totalPeople = Number(detail.adults || timeline.adults || 0) + Number(detail.children || timeline.children || 0);
    overviewEl.innerHTML = `
      <div class="row g-3">
        <div class="col-md-4"><div class="p-3 bg-light rounded-3"><div class="small text-muted">Tên chuyến đi</div><strong>${escapeHtml(detail.trip_title || timeline.trip_title)}</strong></div></div>
        <div class="col-md-4"><div class="p-3 bg-light rounded-3"><div class="small text-muted">Điểm đến</div><strong>${escapeHtml(detail.destination || timeline.destination)}</strong></div></div>
        <div class="col-md-4"><div class="p-3 bg-light rounded-3"><div class="small text-muted">Thời gian</div><strong>${escapeHtml(detail.start_date || timeline.start_date)} - ${escapeHtml(detail.end_date || timeline.end_date)}</strong></div></div>
        <div class="col-md-4"><div class="p-3 bg-light rounded-3"><div class="small text-muted">Số ngày</div><strong>${detail.number_of_days || timeline.number_of_days} ngày</strong></div></div>
        <div class="col-md-4"><div class="p-3 bg-light rounded-3"><div class="small text-muted">Số người</div><strong>${totalPeople} người</strong></div></div>
        <div class="col-md-4"><div class="p-3 bg-light rounded-3"><div class="small text-muted">Trạng thái</div><strong>${statusMeta[detail.status]?.text || plan.status || detail.status}</strong></div></div>
      </div>
      ${plan.members.length ? `
        <h6 class="fw-bold text-dark mt-4 mb-2">Thành viên đồng hành</h6>
        <div class="vstack gap-2">${plan.members.map((member) => `
          <div class="p-3 border rounded-3 bg-light-subtle">
            <strong>${escapeHtml(member.name || 'Thành viên')}</strong>
            <span class="text-muted small ms-2">${escapeHtml(member.role || '')}</span>
            ${member.phone ? `<span class="text-muted small ms-2">${escapeHtml(member.phone)}</span>` : ''}
          </div>`).join('')}</div>` : ''}`;
  }

  function renderCosts(detail, plan) {
    const costEl = document.getElementById('costContent');
    if (!costEl) return;
    const entries = Object.entries(plan.costs || {});
    costEl.innerHTML = `
      <div class="p-3 bg-light rounded-3 mb-3">
        <div class="h4 text-primary fw-bold mb-1">${formatMoney(detail.total_budget, detail.currency)}</div>
        <div class="text-muted small">Tổng chi phí dự kiến</div>
      </div>
      <div class="row g-3">
        ${entries.length ? entries.map(([label, value]) => `
          <div class="col-md-6">
            <div class="d-flex justify-content-between align-items-center p-3 border rounded-3">
              <span>${escapeHtml(label)}</span>
              <strong>${formatMoney(value, detail.currency)}</strong>
            </div>
          </div>`).join('') : '<div class="col-12 text-muted">Chưa có chi tiết chi phí.</div>'}
      </div>`;
  }

  function renderNotes(plan) {
    const notesEl = document.getElementById('notesContent');
    if (!notesEl) return;
    notesEl.innerHTML = `
      ${plan.note ? `<div class="p-3 bg-light rounded-3 mb-3">${escapeHtml(plan.note)}</div>` : ''}
      <h6 class="fw-bold text-dark mb-2">Công việc cần chuẩn bị</h6>
      ${plan.tasks.length ? `
        <div class="vstack gap-2">${plan.tasks.map((task) => `
          <div class="d-flex justify-content-between align-items-center p-3 border rounded-3">
            <div>
              <strong>${escapeHtml(task.task || 'Công việc')}</strong>
              ${task.owner ? `<div class="small text-muted">Phụ trách: ${escapeHtml(task.owner)}</div>` : ''}
            </div>
            <span class="badge bg-primary-subtle text-primary rounded-pill">${escapeHtml(task.status || 'Cần làm')}</span>
          </div>`).join('')}</div>` : '<div class="text-muted">Chưa có công việc chuẩn bị.</div>'}
      ${plan.places.length ? `
        <h6 class="fw-bold text-dark mt-4 mb-2">Địa điểm, nhà hàng, khách sạn</h6>
        <div class="vstack gap-2">${plan.places.map((place) => `
          <div class="p-3 border rounded-3">
            <span class="badge bg-light text-dark border me-2">${escapeHtml(place.type || 'Địa điểm')}</span>
            <strong>${escapeHtml(place.name || '')}</strong>
            ${place.note ? `<div class="small text-muted mt-1">${escapeHtml(place.note)}</div>` : ''}
          </div>`).join('')}</div>` : ''}`;
  }

  async function loadList() {
    if (!listContainer) return;
    try {
      if (listState) listState.textContent = 'Đang tải danh sách...';
      const params = new URLSearchParams({ offset: String((currentPage - 1) * pageSize), limit: String(pageSize) });
      if (searchInput?.value) params.set('search', searchInput.value.trim());
      if (currentStatus) params.set('status', currentStatus);
      const data = await fetchJson(`/api/itineraries?${params.toString()}`);
      const items = data.data || [];
      renderList(items);
      renderPagination(items.length < pageSize ? items.length : currentPage * pageSize);
      if (listState) listState.textContent = items.length ? `Hiển thị ${items.length} chuyến đi.` : 'Không tìm thấy chuyến đi nào.';
    } catch (error) {
      if (listState) listState.textContent = error.message;
      renderEmpty(listContainer, error.message);
    }
  }

  function renderTimeline(timeline) {
    if (!timelineContainer) return;
    if (!timeline.days?.length) {
      timelineContainer.innerHTML = `
        <div class="card border-0 shadow-sm rounded-4 p-4 bg-white text-muted">
          Chưa có lịch trình chi tiết.
        </div>`;
      return;
    }

    timelineContainer.innerHTML = `
      <div class="timeline-wrapper">
        ${timeline.days.map((day) => `
          <div class="timeline-day-block">
            <div class="timeline-day-node"></div>
            <div class="d-flex align-items-center gap-2 mb-3">
              <span class="timeline-day-title">Ngày ${day.day_number}</span>
              <span class="text-muted small">(${escapeHtml(day.itinerary_date || '')})</span>
              <span class="ms-auto fw-bold text-primary small">${day.estimated_daily_cost ? formatMoney(day.estimated_daily_cost, timeline.currency) : ''}</span>
            </div>
            <div class="vstack gap-3">
              ${(day.activities || []).map((act) => `
                <div class="timeline-activity-card">
                  <div class="d-flex flex-column flex-sm-row justify-content-between align-items-sm-start gap-3">
                    <div class="d-flex align-items-start gap-3 flex-grow-1">
                      <span class="activity-time-badge fs-6">${escapeHtml(act.start_time || '08:00')}</span>
                      <div>
                        <h6 class="fw-bold text-dark mb-1">${escapeHtml(act.activity_name)}</h6>
                        <p class="text-muted small mb-1">${escapeHtml(act.description || act.location_name || '')}</p>
                        ${act.address ? `<div class="text-muted small"><i class="bi bi-geo-alt text-danger me-1"></i>${escapeHtml(act.address)}</div>` : ''}
                      </div>
                    </div>
                    <img src="${getDestImage(act.location_name || timeline.destination)}" alt="${escapeHtml(act.activity_name)}" class="activity-thumb-img shadow-sm">
                  </div>
                </div>`).join('')}
            </div>
          </div>`).join('')}
      </div>`;
  }

  async function loadTimeline() {
    if (!itineraryId || !timelineContainer) return;
    try {
      if (timelineState) timelineState.textContent = 'Đang tải chi tiết chuyến đi...';
      const [detail, timelineData] = await Promise.all([
        fetchJson(`/api/itineraries/${itineraryId}`),
        fetchJson(`/api/itineraries/${itineraryId}/timeline`),
      ]);
      const timeline = timelineData.data || timelineData;
      const plan = parsePlanNotes(detail.special_requirements);
      if (detailHeader) {
        const bgImg = getDestImage(detail.destination || timeline.destination);
        const people = Number(detail.adults || 0) + Number(detail.children || 0);
        detailHeader.innerHTML = `
          <div class="card border-0 shadow-sm rounded-4 overflow-hidden itinerary-banner-card p-4 p-md-5" style="background-image: linear-gradient(180deg, rgba(15,23,42,0.4) 0%, rgba(15,23,42,0.85) 100%), url('${bgImg}');">
            <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-end gap-3 position-relative z-2">
              <div>
                <h1 class="fw-bold text-white mb-2 display-6">${escapeHtml(detail.trip_title || timeline.trip_title || timeline.destination)}</h1>
                <p class="text-white-50 mb-0 fs-6">
                  <i class="bi bi-calendar-event me-1"></i>${escapeHtml(detail.start_date || timeline.start_date)} - ${escapeHtml(detail.end_date || timeline.end_date)}
                  <span class="mx-2">•</span>${detail.number_of_days || timeline.number_of_days} ngày
                  <span class="mx-2">•</span>${people} người
                  <span class="mx-2">•</span>${formatMoney(detail.total_budget, detail.currency)}
                </p>
              </div>
              <div class="d-flex flex-wrap gap-2">
                <a class="btn btn-light btn-sm rounded-pill px-3 fw-medium shadow-sm" href="/api/itineraries/${itineraryId}/pdf" target="_blank"><i class="bi bi-file-earmark-pdf me-1"></i>Xuất PDF</a>
                <button class="btn btn-light btn-sm text-danger rounded-pill px-3 fw-medium shadow-sm" id="detailDeleteBtn"><i class="bi bi-trash me-1"></i>Xóa</button>
              </div>
            </div>
          </div>`;
        document.getElementById('detailDeleteBtn')?.addEventListener('click', async () => {
          if (!confirm('Bạn có chắc chắn muốn xóa chuyến đi này không?')) return;
          await fetchJson(`/api/itineraries/${itineraryId}`, { method: 'DELETE' });
          window.location.href = '/itineraries';
        });
      }
      if (timeline.days?.length) renderTimeline(timeline);
      else renderManualTimeline(plan);
      renderOverview(detail, timeline, plan);
      renderCosts(detail, plan);
      renderNotes(plan);
      if (timelineState) timelineState.textContent = '';
    } catch (error) {
      if (timelineState) timelineState.textContent = error.message;
      renderEmpty(timelineContainer, error.message);
    }
  }

  if (listContainer) {
    searchInput?.addEventListener('input', () => {
      currentPage = 1;
      loadList();
    });
    statusTabs?.querySelectorAll('button[data-status]').forEach((btn) => {
      btn.addEventListener('click', (event) => {
        statusTabs.querySelectorAll('.nav-link').forEach((item) => item.classList.remove('active'));
        event.currentTarget.classList.add('active');
        currentStatus = event.currentTarget.dataset.status;
        currentPage = 1;
        loadList();
      });
    });
    refreshListBtn?.addEventListener('click', () => loadList());
    loadList();
  }

  if (timelineContainer) loadTimeline();
})();
