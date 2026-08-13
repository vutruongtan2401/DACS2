(function () {
  const token = localStorage.getItem('access_token');
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  async function fetchJson(url) {
    const response = await fetch(url, { headers });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.message || 'Khong the tai du lieu dashboard');
    }
    return data;
  }

  function statCard(title, value, icon, tone = 'warning') {
    return `
      <div class="col-md-6 col-xl-3">
        <div class="panel h-100">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="text-muted small">${title}</div>
              <div class="fs-3 fw-bold">${value}</div>
            </div>
            <div class="fs-2 text-${tone}"><i class="bi ${icon}"></i></div>
          </div>
        </div>
      </div>`;
  }

  function fillTable(selector, rows, colspan = 5) {
    const tbody = document.getElementById(selector);
    if (!tbody) return;
    tbody.innerHTML = rows.join('') || `<tr><td colspan="${colspan}" class="text-center text-muted">Khong co du lieu</td></tr>`;
  }

  function buildChart(canvasId, labels, data, label, color) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === 'undefined') return;
    new Chart(canvas, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label,
          data,
          borderColor: color,
          backgroundColor: `${color}33`,
          tension: 0.35,
          fill: true,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#fff' } } },
        scales: { x: { ticks: { color: '#fff' } }, y: { ticks: { color: '#fff' } } },
      },
    });
  }

  async function loadDashboard() {
    const overview = await fetchJson('/api/admin/statistics/overview');
    const users = await fetchJson('/api/admin/users?limit=50');
    const itineraries = await fetchJson('/api/admin/itineraries?limit=50');

    const statsCards = document.getElementById('statsCards');
    if (statsCards) {
      statsCards.innerHTML = [
        statCard('Tong nguoi dung', overview.total_users ?? 0, 'bi-people-fill'),
        statCard('Nguoi dung moi', overview.new_users ?? 0, 'bi-person-add'),
        statCard('Tong chuyen di', overview.total_itineraries ?? 0, 'bi-map-fill'),
        statCard('Hoan thanh', overview.generated_itineraries ?? 0, 'bi-check-circle-fill', 'success'),
      ].join('');
    }

    fillTable('usersTable', (users.data || []).map((item) => `<tr><td>${item.id}</td><td>${item.full_name}</td><td>${item.email}</td><td>${item.role}</td><td>${item.status}</td></tr>`));
    fillTable('itinerariesTable', (itineraries.data || []).map((item) => `<tr><td>${item.id}</td><td>${item.trip_title}</td><td>${item.destination}</td><td>${item.start_date}</td><td>${item.end_date}</td><td>${item.spent_amount || 0}</td><td>${item.status}</td></tr>`), 7);
    buildChart('usersChart', ['T1', 'T2', 'T3', 'T4', 'T5'], [1, 2, 3, 4, 5], 'Nguoi dung', '#66d9ef');
    buildChart('itinerariesChart', ['T1', 'T2', 'T3', 'T4', 'T5'], [2, 3, 4, 6, 8], 'Chuyen di', '#f7a84b');
  }

  loadDashboard().catch((error) => {
    console.error(error);
  });
})();
