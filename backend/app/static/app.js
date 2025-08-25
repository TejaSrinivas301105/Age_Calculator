const apiBase = '';

const resultsCard = document.getElementById('results-card');
const resultsDiv = document.getElementById('results');
const statusCard = document.getElementById('status-card');
const statusDiv = document.getElementById('status');

function availabilityPill(seats, standing) {
  if (seats === 0 && standing === 0) {
    return '<span class="pill full">FULL</span>';
  }
  if (seats <= 3 || standing <= 3) {
    return `<span class="pill warn">Limited: ${seats} seat, ${standing} stand</span>`;
  }
  return `<span class="pill ok">Available: ${seats} seat, ${standing} stand</span>`;
}

function renderResults(items) {
  if (!Array.isArray(items) || items.length === 0) {
    resultsDiv.innerHTML = '<p class="muted">No buses found for this route.</p>';
    resultsCard.hidden = false;
    return;
  }

  resultsDiv.innerHTML = items.map((b) => {
    const pill = availabilityPill(b.seats_available, b.standing_available);
    const loc = b.last_stop_name ? `Stop: ${b.last_stop_name}` : (b.last_latitude ? `(${b.last_latitude.toFixed(4)}, ${b.last_longitude.toFixed(4)})` : 'Location: unknown');
    return `
      <div class="bus-row">
        <div>
          <div><strong>${b.registration_number}</strong> — ${b.route_name}</div>
          <div class="muted">${loc}</div>
        </div>
        <div>${pill}</div>
        <div class="row-actions">
          <button data-busid="${b.bus_id}" class="view-btn">View</button>
        </div>
      </div>
    `;
  }).join('');

  resultsDiv.querySelectorAll('.view-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.getAttribute('data-busid');
      const res = await fetch(`${apiBase}/bus/${id}`);
      const data = await res.json();
      renderStatus(data);
      statusCard.hidden = false;
      statusCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
  resultsCard.hidden = false;
}

function renderStatus(b) {
  const pill = availabilityPill(b.seats_available, b.standing_available);
  const loc = b.last_stop_name ? `Stop: ${b.last_stop_name}` : (b.last_latitude ? `(${Number(b.last_latitude).toFixed(4)}, ${Number(b.last_longitude).toFixed(4)})` : 'Location: unknown');
  statusDiv.innerHTML = `
    <div class="bus-row">
      <div>
        <div><strong>${b.registration_number}</strong> — ${b.route_name}</div>
        <div class="muted">${loc}</div>
      </div>
      <div>${pill}</div>
      <div class="muted">${b.seats_occupied}/${b.capacity_seated} seated, ${b.standing_occupied}/${b.capacity_standing} standing</div>
    </div>
  `;
}

document.getElementById('search-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  statusCard.hidden = true;
  const fromStop = document.getElementById('fromStop').value.trim();
  const toStop = document.getElementById('toStop').value.trim();
  if (!fromStop || !toStop) return;
  resultsDiv.innerHTML = '<p class="muted">Searching…</p>';
  resultsCard.hidden = false;
  try {
    const res = await fetch(`${apiBase}/search?from_stop=${encodeURIComponent(fromStop)}&to_stop=${encodeURIComponent(toStop)}`);
    if (!res.ok) {
      resultsDiv.innerHTML = '<p class="muted">No results or error.</p>';
      return;
    }
    const data = await res.json();
    renderResults(data);
  } catch (err) {
    resultsDiv.innerHTML = '<p class="muted">Network error.</p>';
  }
});
