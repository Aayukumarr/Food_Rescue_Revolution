// public/app.js - Complete Frontend Application Logic for Food Rescue Revolution

// Application State
const state = {
  currentRole: 'donor', // 'donor', 'recipient', 'volunteer', 'admin'
  userProfile: {
    donor: { id: 'usr-donor-1', name: 'Chef Rajesh Sharma', org: 'The Grand Heritage Banquet & Hotel' },
    recipient: { id: 'usr-rec-1', name: 'Sister Mary Teresa', org: 'Asha Child Hope Home & Orphanage' },
    volunteer: { id: 'usr-vol-1', name: 'Kabir Das', org: 'Food Runners Youth Chapter' },
    admin: { id: 'usr-admin-1', name: 'Antigravity Coordinator', org: 'Food Rescue Revolution HQ' }
  },
  donations: [],
  aidRequests: [],
  alerts: [],
  impact: null,
  leaderboard: null,
  filter: {
    search: '',
    category: 'all',
    food_type: 'all',
    status: 'all'
  },
  map: null,
  markersLayer: null,
  charts: {
    impactTrend: null,
    categoryDoughnut: null
  }
};

// Notification Sound / Haptic simulator
function triggerToast(title, message, urgency = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast-msg ${urgency === 'emergency' ? 'emergency' : ''}`;
  
  const icon = urgency === 'emergency' ? '🚨' : (urgency === 'high' ? '⚡' : '✅');

  toast.innerHTML = `
    <div style="font-size: 1.5rem;">${icon}</div>
    <div style="flex: 1;">
      <h4 style="font-weight: 700; font-size: 0.95rem; margin-bottom: 2px; color: ${urgency === 'emergency' ? '#dc2626' : '#0f172a'};">${escapeHtml(title)}</h4>
      <p style="font-size: 0.85rem; color: #475569; line-height: 1.3;">${escapeHtml(message)}</p>
    </div>
    <button onclick="this.parentElement.remove()" style="background: none; border: none; font-size: 1.1rem; color: #94a3b8; cursor: pointer;">&times;</button>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    if (toast.parentElement) toast.remove();
  }, 6500);
}

// Utility: HTML escape
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Format relative time or countdown
function formatCountdown(expiryIso) {
  const diffMs = new Date(expiryIso) - Date.now();
  if (diffMs <= 0) {
    return { text: 'EXPIRED', class: 'countdown-urgent', hours: 0 };
  }
  const totalSeconds = Math.floor(diffMs / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  const pad = (n) => String(n).padStart(2, '0');
  const text = `${pad(hours)}h ${pad(minutes)}m ${pad(seconds)}s left`;

  if (hours < 3) {
    return { text: `🔥 ${text}`, class: 'countdown-urgent', hours };
  } else if (hours < 8) {
    return { text: `⏳ ${text}`, class: 'countdown-moderate', hours };
  }
  return { text: `🌱 ${text}`, class: 'countdown-safe', hours };
}

// Initialize Application
document.addEventListener('DOMContentLoaded', async () => {
  initRoleSwitcher();
  initNavigation();
  initMap();
  initSSE();
  initModalListeners();
  initAiAdvisor();

  await loadAllData();

  // Periodic Countdown Refresh every second
  setInterval(() => {
    renderCountdowns();
  }, 1000);
});

// Role Switcher Setup
function initRoleSwitcher() {
  const select = document.getElementById('role-select');
  if (!select) return;

  select.value = state.currentRole;
  select.addEventListener('change', (e) => {
    state.currentRole = e.target.value;
    updateRoleUI();
  });
  updateRoleUI();
}

function updateRoleUI() {
  const user = state.userProfile[state.currentRole];
  const roleBadge = document.getElementById('current-user-display');
  if (roleBadge) {
    roleBadge.innerHTML = `
      <span style="font-weight: 600;">${user.name}</span>
      <span style="font-size: 0.75rem; background: #e2e8f0; color: #334155; padding: 2px 8px; border-radius: 9999px; margin-left: 6px;">${user.org}</span>
    `;
  }

  // Update dynamic permissions on action buttons
  renderDonationsList();
  renderDeliveriesSection();
}

// Navigation Tabs
function initNavigation() {
  const tabs = document.querySelectorAll('.nav-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = tab.getAttribute('data-target');
      showSection(targetId);

      tabs.forEach(t => t.classList.remove('active', 'border-emerald-600', 'text-emerald-700', 'bg-emerald-50'));
      tab.classList.add('active', 'border-emerald-600', 'text-emerald-700', 'bg-emerald-50');
    });
  });
}

function showSection(sectionId) {
  const sections = document.querySelectorAll('.content-section');
  sections.forEach(s => s.classList.add('hidden'));

  const active = document.getElementById(sectionId);
  if (active) {
    active.classList.remove('hidden');
    // If map section, resize map after container becomes visible
    if (sectionId === 'section-map' && state.map) {
      setTimeout(() => state.map.invalidateSize(), 200);
    }
  }
}

// OpenStreetMap Initialization with Leaflet
function initMap() {
  const mapContainer = document.getElementById('rescue-map');
  if (!mapContainer || typeof L === 'undefined') return;

  // Center on Central Delhi
  state.map = L.map('rescue-map', {
    zoomControl: true,
    scrollWheelZoom: true
  }).setView([28.6139, 77.2090], 12);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors | Food Rescue Revolution'
  }).addTo(state.map);

  state.markersLayer = L.layerGroup().addTo(state.map);

  // Map Filter Radii
  const radiusSelect = document.getElementById('map-radius-filter');
  if (radiusSelect) {
    radiusSelect.addEventListener('change', renderMapMarkers);
  }

  // "Locate Me" button
  const locateBtn = document.getElementById('btn-locate-me');
  if (locateBtn) {
    locateBtn.addEventListener('click', () => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            const { latitude, longitude } = pos.coords;
            state.map.setView([latitude, longitude], 14);
            L.circle([latitude, longitude], {
              radius: 500,
              color: '#0ea5e9',
              fillColor: '#38bdf8',
              fillOpacity: 0.2
            }).addTo(state.map);
            triggerToast('Location Detected', 'Zoomed into your current area.', 'info');
          },
          () => {
            triggerToast('Location Alert', 'Using default metro coordinates (Delhi Center)', 'info');
          }
        );
      }
    });
  }
}

function renderMapMarkers() {
  if (!state.map || !state.markersLayer) return;
  state.markersLayer.clearLayers();

  // Add Partner Shelters
  const shelters = [
    { name: 'Asha Child Hope Home & Orphanage', lat: 28.5916, lng: 77.2219, type: 'Orphanage & Children Shelter', capacity: '120 children' },
    { name: 'Langar Seva Community Food Bank', lat: 28.6514, lng: 77.1907, type: 'Community Kitchen & Food Bank', capacity: '500+ daily' },
    { name: 'Prerna Slum Relief Hub', lat: 28.5284, lng: 77.2793, type: 'Evening Relief School', capacity: '180 children' }
  ];

  shelters.forEach(s => {
    const icon = L.divIcon({
      className: 'custom-pin pin-shelter',
      html: '<div style="font-size:16px;">🏛️</div>',
      iconSize: [36, 36],
      iconAnchor: [18, 18]
    });

    const marker = L.marker([s.lat, s.lng], { icon });
    marker.bindPopup(`
      <div style="font-family: inherit; min-width: 200px;">
        <span style="background: #e0f2fe; color: #0369a1; font-size: 0.75rem; font-weight: 700; padding: 2px 6px; border-radius: 4px;">REGISTERED SHELTER</span>
        <h3 style="font-weight: 700; font-size: 1rem; margin: 4px 0;">${escapeHtml(s.name)}</h3>
        <p style="font-size: 0.82rem; color: #64748b; margin-bottom: 6px;">${s.type} • Capacity: ${s.capacity}</p>
        <button onclick="openAidRequestModal('${escapeHtml(s.name)}')" style="background: #0284c7; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-size: 0.8rem; cursor: pointer; font-weight: 600; width: 100%;">Direct Food Transfer</button>
      </div>
    `);
    state.markersLayer.addLayer(marker);
  });

  // Add Surplus Food Donation Pins
  state.donations.forEach(d => {
    if (d.status === 'delivered') return;

    let pinClass = 'pin-available';
    let iconChar = '🍲';

    if (d.status === 'claimed') {
      pinClass = 'pin-claimed';
      iconChar = '📦';
    } else if (d.status === 'in_transit') {
      pinClass = 'pin-in-transit';
      iconChar = '🛵';
    }

    const icon = L.divIcon({
      className: `custom-pin ${pinClass}`,
      html: `<div style="font-size:16px;">${iconChar}</div>`,
      iconSize: [38, 38],
      iconAnchor: [19, 19]
    });

    const countdown = formatCountdown(d.expiry_time);

    const marker = L.marker([d.lat, d.lng], { icon });
    marker.bindPopup(`
      <div style="font-family: inherit; min-width: 240px; padding: 4px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 4px;">
          <span style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; padding: 2px 6px; border-radius: 4px; background: ${d.status === 'available' ? '#dcfce7; color:#15803d' : '#fef3c7; color:#b45309'};">
            ${d.status.replace('_', ' ')}
          </span>
          <span style="font-size: 0.75rem; font-weight: 600; color: #b91c1c;">${countdown.text}</span>
        </div>
        <h4 style="font-weight: 700; font-size: 0.95rem; margin: 4px 0;">${escapeHtml(d.title)}</h4>
        <p style="font-size: 0.82rem; color: #475569; margin-bottom: 6px;">
          <strong>${d.servings} servings</strong> (${d.weight_kg} kg) • ${d.category.replace('_', ' ')}
        </p>
        <p style="font-size: 0.78rem; color: #64748b; margin-bottom: 10px;">📍 ${escapeHtml(d.pickup_address)}</p>
        ${d.status === 'available' ? `
          <button onclick="claimDonation('${d.id}')" style="background: #10b981; color: white; border: none; padding: 7px 12px; border-radius: 6px; font-size: 0.82rem; cursor: pointer; font-weight: 700; width: 100%;">
            Claim Surplus as NGO
          </button>
        ` : (d.status === 'claimed' ? `
          <button onclick="assignVolunteer('${d.id}')" style="background: #f59e0b; color: white; border: none; padding: 7px 12px; border-radius: 6px; font-size: 0.82rem; cursor: pointer; font-weight: 700; width: 100%;">
            Deliver as Volunteer
          </button>
        ` : `
          <div style="font-size: 0.8rem; color: #8b5cf6; font-weight: 600; text-align: center;">🛵 In Transit with ${escapeHtml(d.volunteer_name || 'Volunteer')}</div>
        `)}
      </div>
    `);
    state.markersLayer.addLayer(marker);
  });
}

// Server-Sent Events (SSE) Live Feed Listener
function initSSE() {
  if (typeof EventSource === 'undefined') return;

  const es = new EventSource('/api/events');
  const sseStatus = document.getElementById('sse-status-badge');

  es.onopen = () => {
    if (sseStatus) {
      sseStatus.innerHTML = '<span class="live-pulse"></span> <span class="text-emerald-700 font-semibold text-xs">Live Sync Active</span>';
    }
  };

  es.addEventListener('new_donation', (e) => {
    const donation = JSON.parse(e.data);
    state.donations.unshift(donation);
    renderDonationsList();
    renderMapMarkers();
    loadImpactMetrics();
    triggerToast('New Surplus Food Available!', `${donation.title} (${donation.servings} portions) listed at ${donation.pickup_address}`, 'high');
  });

  es.addEventListener('donation_claimed', (e) => {
    const updated = JSON.parse(e.data);
    updateLocalDonation(updated);
    renderDonationsList();
    renderMapMarkers();
    renderDeliveriesSection();
    triggerToast('Surplus Claimed!', `${updated.recipient_name} claimed ${updated.title}. Ready for volunteer pickup!`, 'high');
  });

  es.addEventListener('volunteer_assigned', (e) => {
    const updated = JSON.parse(e.data);
    updateLocalDonation(updated);
    renderDonationsList();
    renderMapMarkers();
    renderDeliveriesSection();
    triggerToast('Volunteer En Route 🛵', `${updated.volunteer_name} accepted pickup for ${updated.title}!`, 'info');
  });

  es.addEventListener('donation_delivered', (e) => {
    const updated = JSON.parse(e.data);
    updateLocalDonation(updated);
    renderDonationsList();
    renderMapMarkers();
    renderDeliveriesSection();
    loadImpactMetrics();
    loadLeaderboard();
    triggerToast('Food Successfully Rescued! 🎉', `${updated.servings} meals delivered with zero waste!`, 'info');
  });

  es.addEventListener('new_alert', (e) => {
    const alert = JSON.parse(e.data);
    state.alerts.unshift(alert);
    renderAlerts();
    if (alert.urgency === 'emergency') {
      triggerToast('EMERGENCY FOOD RESCUE ALERT', alert.message, 'emergency');
    }
  });

  es.addEventListener('database_reset', () => {
    loadAllData();
    triggerToast('Database Reseeded', 'Platform restored to initial sample state.', 'info');
  });

  es.onerror = () => {
    if (sseStatus) {
      sseStatus.innerHTML = '<span class="text-amber-600 font-semibold text-xs">Reconnecting...</span>';
    }
  };
}

function updateLocalDonation(updated) {
  const index = state.donations.findIndex(d => d.id === updated.id);
  if (index !== -1) {
    state.donations[index] = updated;
  } else {
    state.donations.unshift(updated);
  }
}

// Load all API Data
async function loadAllData() {
  await Promise.all([
    loadDonations(),
    loadImpactMetrics(),
    loadLeaderboard(),
    loadAlerts(),
    loadAidRequests()
  ]);
  renderMapMarkers();
}

async function loadDonations() {
  try {
    const res = await fetch('/api/donations');
    if (!res.ok) throw new Error('Failed to load donations');
    state.donations = await res.json();
    renderDonationsList();
    renderDeliveriesSection();
  } catch (err) {
    console.error(err);
  }
}

async function loadImpactMetrics() {
  try {
    const res = await fetch('/api/impact');
    if (!res.ok) throw new Error('Failed to load impact');
    state.impact = await res.json();
    renderImpactStats();
    renderImpactCharts();
  } catch (err) {
    console.error(err);
  }
}

async function loadLeaderboard() {
  try {
    const res = await fetch('/api/leaderboard');
    if (!res.ok) throw new Error('Failed to load leaderboard');
    state.leaderboard = await res.json();
    renderLeaderboard();
  } catch (err) {
    console.error(err);
  }
}

async function loadAlerts() {
  try {
    const res = await fetch('/api/alerts');
    if (!res.ok) throw new Error('Failed to load alerts');
    state.alerts = await res.json();
    renderAlerts();
  } catch (err) {
    console.error(err);
  }
}

async function loadAidRequests() {
  try {
    const res = await fetch('/api/aid-requests');
    if (!res.ok) throw new Error('Failed to load aid requests');
    state.aidRequests = await res.json();
    renderAidRequests();
  } catch (err) {
    console.error(err);
  }
}

// Render Listings & Cards
function renderDonationsList() {
  const container = document.getElementById('donations-container');
  if (!container) return;

  const searchInput = document.getElementById('filter-search');
  const categorySelect = document.getElementById('filter-category');
  const typeSelect = document.getElementById('filter-food-type');
  const statusSelect = document.getElementById('filter-status');

  const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
  const cat = categorySelect ? categorySelect.value : 'all';
  const foodType = typeSelect ? typeSelect.value : 'all';
  const statusVal = statusSelect ? statusSelect.value : 'all';

  const filtered = state.donations.filter(d => {
    if (searchTerm && !d.title.toLowerCase().includes(searchTerm) && !d.pickup_address.toLowerCase().includes(searchTerm)) {
      return false;
    }
    if (cat !== 'all' && d.category !== cat) return false;
    if (foodType !== 'all' && d.food_type !== foodType) return false;
    if (statusVal !== 'all' && d.status !== statusVal) return false;
    return true;
  });

  const countBadge = document.getElementById('donations-count-badge');
  if (countBadge) {
    countBadge.textContent = `${filtered.length} listings available`;
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 48px; background: white; border-radius: 1rem; border: 1px dashed #cbd5e1;">
        <div style="font-size: 3rem; margin-bottom: 12px;">🥗</div>
        <h3 style="font-size: 1.25rem; font-weight: 700; color: #1e293b;">No matching food surplus listings found</h3>
        <p style="color: #64748b; margin-top: 4px;">Try clearing filters or post a new food donation!</p>
        <button onclick="document.getElementById('btn-open-donate-modal').click()" style="margin-top: 16px; background: #10b981; color: white; padding: 8px 18px; border-radius: 8px; font-weight: 600; border: none; cursor: pointer;">
          + Post Food Donation
        </button>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(d => {
    const countdown = formatCountdown(d.expiry_time);
    const categoryIcons = {
      cooked_meals: '🍲 Cooked Meals',
      bakery: '🥖 Bakery & Breads',
      fresh_produce: '🥦 Fresh Produce',
      dairy: '🥛 Dairy',
      packaged: '📦 Packaged Goods'
    };

    const dietaryBadge = d.food_type === 'veg'
      ? '<span style="background: #ecfdf5; color: #047857; font-weight: 700; font-size: 0.72rem; padding: 2px 8px; border-radius: 9999px; border: 1px solid #a7f3d0;">🟢 100% VEG</span>'
      : (d.food_type === 'vegan'
        ? '<span style="background: #f0fdf4; color: #15803d; font-weight: 700; font-size: 0.72rem; padding: 2px 8px; border-radius: 9999px; border: 1px solid #86efac;">🌱 VEGAN</span>'
        : '<span style="background: #fff1f2; color: #be123c; font-weight: 700; font-size: 0.72rem; padding: 2px 8px; border-radius: 9999px; border: 1px solid #fecdd3;">🔴 NON-VEG</span>');

    return `
      <div class="food-card" data-donation-id="${d.id}">
        <div style="position: relative; height: 180px; overflow: hidden; background: #e2e8f0;">
          <img src="${escapeHtml(d.image_url || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80')}"
               alt="${escapeHtml(d.title)}"
               style="width: 100%; height: 100%; object-fit: cover;"
               onerror="this.src='https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80'" />
          
          <div style="position: absolute; top: 12px; left: 12px; display: flex; gap: 6px;">
            ${dietaryBadge}
          </div>

          <div style="position: absolute; top: 12px; right: 12px;">
            <span class="countdown-badge ${countdown.class}" style="padding: 4px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;" data-expiry="${d.expiry_time}">
              ${countdown.text}
            </span>
          </div>

          <div style="position: absolute; bottom: 8px; left: 12px; background: rgba(15, 23, 42, 0.8); color: white; padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600;">
            ${categoryIcons[d.category] || d.category}
          </div>
        </div>

        <div style="padding: 18px;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <h3 style="font-size: 1.1rem; font-weight: 700; color: #0f172a; line-height: 1.3; margin-bottom: 4px;">
              ${escapeHtml(d.title)}
            </h3>
          </div>

          <p style="font-size: 0.85rem; color: #475569; margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
            ${escapeHtml(d.description || 'Pristine quality surplus food prepared in certified commercial kitchen.')}
          </p>

          <div style="background: #f8fafc; border-radius: 8px; padding: 10px; margin-bottom: 14px; font-size: 0.82rem; border: 1px solid #f1f5f9;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span style="color: #64748b;">Portions / Servings:</span>
              <strong style="color: #0f172a; font-size: 0.9rem;">${d.servings} Meals (${d.weight_kg} kg)</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span style="color: #64748b;">Donor:</span>
              <span style="font-weight: 600; color: #0f172a;">${escapeHtml(d.donor_name)}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span style="color: #64748b;">Pickup Location:</span>
              <span style="font-weight: 500; color: #334155; max-width: 170px; text-align: right; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;" title="${escapeHtml(d.pickup_address)}">
                📍 ${escapeHtml(d.pickup_address)}
              </span>
            </div>
          </div>

          <!-- Status and Action Bar -->
          <div style="display: flex; align-items: center; justify-content: space-between; pt-2;">
            <div>
              ${getStatusPill(d.status)}
            </div>

            <div style="display: flex; gap: 8px;">
              ${d.status === 'available' ? `
                <button onclick="claimDonation('${d.id}')"
                        style="background: #10b981; hover:background: #059669; color: white; border: none; padding: 7px 14px; border-radius: 8px; font-weight: 700; font-size: 0.82rem; cursor: pointer; display: flex; align-items: center; gap: 4px;">
                  Claim Food 🤝
                </button>
              ` : (d.status === 'claimed' ? `
                <button onclick="assignVolunteer('${d.id}')"
                        style="background: #f59e0b; color: white; border: none; padding: 7px 14px; border-radius: 8px; font-weight: 700; font-size: 0.82rem; cursor: pointer; display: flex; align-items: center; gap: 4px;">
                  Deliver 🛵
                </button>
              ` : (d.status === 'in_transit' ? `
                <button onclick="openVerifyDeliveryModal('${d.id}', '${escapeHtml(d.verification_code || '')}')"
                        style="background: #8b5cf6; color: white; border: none; padding: 7px 14px; border-radius: 8px; font-weight: 700; font-size: 0.82rem; cursor: pointer; display: flex; align-items: center; gap: 4px;">
                  Verify Delivery 🔑
                </button>
              ` : `
                <span style="color: #10b981; font-weight: 700; font-size: 0.85rem;">🎉 Rescued</span>
              `))}
            </div>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function getStatusPill(status) {
  if (status === 'available') {
    return `<span style="background: #dcfce7; color: #166534; font-size: 0.75rem; font-weight: 700; padding: 4px 8px; border-radius: 6px;">● Available</span>`;
  } else if (status === 'claimed') {
    return `<span style="background: #fef3c7; color: #92400e; font-size: 0.75rem; font-weight: 700; padding: 4px 8px; border-radius: 6px;">● Claimed (Awaiting Pickup)</span>`;
  } else if (status === 'in_transit') {
    return `<span style="background: #ede9fe; color: #6d28d9; font-size: 0.75rem; font-weight: 700; padding: 4px 8px; border-radius: 6px;">● In Transit 🛵</span>`;
  } else if (status === 'delivered') {
    return `<span style="background: #e0f2fe; color: #075985; font-size: 0.75rem; font-weight: 700; padding: 4px 8px; border-radius: 6px;">✓ Safely Delivered</span>`;
  }
  return `<span style="background: #f1f5f9; color: #475569; font-size: 0.75rem; font-weight: 700; padding: 4px 8px; border-radius: 6px;">${status}</span>`;
}

// Render dynamic countdowns across cards
function renderCountdowns() {
  const badges = document.querySelectorAll('.countdown-badge[data-expiry]');
  badges.forEach(badge => {
    const expiry = badge.getAttribute('data-expiry');
    const cd = formatCountdown(expiry);
    badge.textContent = cd.text;
    badge.className = `countdown-badge ${cd.class}`;
  });
}

// Volunteer Delivery Mission Center Section
function renderDeliveriesSection() {
  const container = document.getElementById('volunteer-deliveries-list');
  if (!container) return;

  const activeDeliveries = state.donations.filter(d => d.status === 'claimed' || d.status === 'in_transit');

  if (activeDeliveries.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px; background: white; border-radius: 1rem; border: 1px dashed #cbd5e1;">
        <div style="font-size: 2.5rem; margin-bottom: 8px;">🛵</div>
        <h4 style="font-weight: 700; color: #1e293b;">No active delivery runs at this moment</h4>
        <p style="color: #64748b; font-size: 0.9rem;">Once an NGO claims a food listing, pickup runs will appear here for volunteers.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = activeDeliveries.map(d => `
    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: var(--card-shadow); margin-bottom: 16px;">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
        <div>
          <span style="font-size: 0.75rem; font-weight: 700; background: ${d.status === 'in_transit' ? '#ede9fe; color: #6d28d9;' : '#fef3c7; color: #b45309;'} padding: 3px 8px; border-radius: 6px;">
            ${d.status === 'in_transit' ? '🛵 IN TRANSIT' : '📦 READY FOR PICKUP'}
          </span>
          <h4 style="font-size: 1.15rem; font-weight: 700; color: #0f172a; margin-top: 6px;">${escapeHtml(d.title)}</h4>
        </div>
        <div style="text-align: right;">
          <span style="font-size: 1.1rem; font-weight: 800; color: #10b981;">${d.servings} Servings</span>
          <div style="font-size: 0.78rem; color: #64748b;">(${d.weight_kg} kg weight)</div>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; background: #f8fafc; padding: 14px; border-radius: 8px; margin-bottom: 16px;">
        <div>
          <div style="font-size: 0.75rem; color: #64748b; font-weight: 600;">PICKUP LOCATION (DONOR)</div>
          <div style="font-weight: 700; color: #1e293b; margin-top: 2px;">${escapeHtml(d.donor_name)}</div>
          <div style="font-size: 0.82rem; color: #475569;">📍 ${escapeHtml(d.pickup_address)}</div>
        </div>
        <div>
          <div style="font-size: 0.75rem; color: #64748b; font-weight: 600;">DELIVER TO (RECIPIENT NGO)</div>
          <div style="font-weight: 700; color: #1e293b; margin-top: 2px;">${escapeHtml(d.recipient_name || 'Designated Shelter')}</div>
          <div style="font-size: 0.82rem; color: #475569;">${escapeHtml(d.claim_notes || 'Shelter dinner distribution')}</div>
        </div>
        <div>
          <div style="font-size: 0.75rem; color: #64748b; font-weight: 600;">FOOD SAFETY REQUIREMENT</div>
          <div style="font-size: 0.82rem; color: #334155; margin-top: 2px;">${escapeHtml(d.storage_instructions || 'Insulated food carriers')}</div>
        </div>
      </div>

      <div style="display: flex; justify-content: flex-end; gap: 10px;">
        ${d.status === 'claimed' ? `
          <button onclick="assignVolunteer('${d.id}')"
                  style="background: #f59e0b; color: white; border: none; padding: 9px 18px; border-radius: 8px; font-weight: 700; cursor: pointer; font-size: 0.88rem;">
            🛵 Accept Pickup Run
          </button>
        ` : `
          <button onclick="openVerifyDeliveryModal('${d.id}', '${escapeHtml(d.verification_code || '')}')"
                  style="background: #10b981; color: white; border: none; padding: 9px 18px; border-radius: 8px; font-weight: 700; cursor: pointer; font-size: 0.88rem;">
            ✓ Confirm Recipient Drop-off (Enter OTP)
          </button>
        `}
      </div>
    </div>
  `).join('');
}

// Render Impact Counters
function renderImpactStats() {
  if (!state.impact) return;
  const { total_meals, total_kg, co2_avoided_kg, water_saved_liters, total_deliveries } = state.impact;

  animateCounter('stat-meals-count', total_meals);
  animateCounter('stat-waste-count', total_kg);
  animateCounter('stat-co2-count', co2_avoided_kg);
  animateCounter('stat-water-count', water_saved_liters);
  animateCounter('stat-deliveries-count', total_deliveries);

  // Environmental equivalents calculations
  const treesElement = document.getElementById('stat-trees-equiv');
  if (treesElement) {
    // 1 tree absorbs ~22 kg CO2 per year
    const trees = Math.round(co2_avoided_kg / 22);
    treesElement.textContent = `🌳 Equivalent to planting ${trees} mature trees`;
  }
}

function animateCounter(elementId, targetValue) {
  const el = document.getElementById(elementId);
  if (!el) return;

  const current = parseInt(el.textContent.replace(/[^0-9]/g, ''), 10) || 0;
  const diff = targetValue - current;
  if (diff === 0) {
    el.textContent = targetValue.toLocaleString();
    return;
  }

  let step = Math.ceil(diff / 20);
  let val = current;

  const timer = setInterval(() => {
    val += step;
    if ((step > 0 && val >= targetValue) || (step < 0 && val <= targetValue)) {
      el.textContent = targetValue.toLocaleString();
      clearInterval(timer);
    } else {
      el.textContent = val.toLocaleString();
    }
  }, 25);
}

// Chart.js Impact Visualizations
function renderImpactCharts() {
  if (typeof Chart === 'undefined' || !state.impact) return;

  // 1. Monthly Food Rescued Trend
  const trendCtx = document.getElementById('chart-impact-trend');
  if (trendCtx) {
    if (state.charts.impactTrend) state.charts.impactTrend.destroy();
    state.charts.impactTrend = new Chart(trendCtx, {
      type: 'line',
      data: {
        labels: ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct (Live)'],
        datasets: [
          {
            label: 'Meals Rescued',
            data: [620, 1150, 1890, 2400, 3100, state.impact.total_meals],
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            fill: true,
            tension: 0.4,
            borderWidth: 3
          },
          {
            label: 'CO2 Prevented (kg)',
            data: [450, 820, 1340, 1750, 2200, state.impact.co2_avoided_kg],
            borderColor: '#0284c7',
            backgroundColor: 'rgba(2, 132, 199, 0.05)',
            fill: true,
            tension: 0.4,
            borderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'top' }
        },
        scales: {
          y: { beginAtZero: true }
        }
      }
    });
  }

  // 2. Category Breakdown Doughnut Chart
  const categoryCtx = document.getElementById('chart-category-doughnut');
  if (categoryCtx) {
    if (state.charts.categoryDoughnut) state.charts.categoryDoughnut.destroy();

    const breakdown = state.impact.categoryBreakdown || [];
    const labels = breakdown.map(b => b.category.replace('_', ' ').toUpperCase());
    const counts = breakdown.map(b => b.total_servings || b.count);

    state.charts.categoryDoughnut = new Chart(categoryCtx, {
      type: 'doughnut',
      data: {
        labels: labels.length ? labels : ['COOKED MEALS', 'BAKERY', 'PRODUCE', 'DAIRY'],
        datasets: [{
          data: counts.length ? counts : [65, 20, 10, 5],
          backgroundColor: ['#10b981', '#f59e0b', '#06b6d4', '#8b5cf6', '#ec4899']
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' }
        }
      }
    });
  }
}

// Render Leaderboard
function renderLeaderboard() {
  if (!state.leaderboard) return;
  const donorsTable = document.getElementById('leaderboard-donors-body');
  const volunteersTable = document.getElementById('leaderboard-volunteers-body');

  if (donorsTable && state.leaderboard.topDonors) {
    donorsTable.innerHTML = state.leaderboard.topDonors.map((d, i) => `
      <tr style="border-bottom: 1px solid #f1f5f9;">
        <td style="padding: 12px; font-weight: 700; color: ${i === 0 ? '#eab308' : '#64748b'};">#${i + 1}</td>
        <td style="padding: 12px;">
          <div style="font-weight: 700; color: #0f172a;">${escapeHtml(d.organization || d.name)}</div>
          <div style="font-size: 0.78rem; color: #64748b;">${escapeHtml(d.badge || 'Donor Partner')}</div>
        </td>
        <td style="padding: 12px; font-weight: 800; color: #10b981;">${d.rescued_meals_count.toLocaleString()} meals</td>
        <td style="padding: 12px; font-size: 0.85rem; color: #475569;">⭐ ${d.rating.toFixed(1)}</td>
      </tr>
    `).join('');
  }

  if (volunteersTable && state.leaderboard.topVolunteers) {
    volunteersTable.innerHTML = state.leaderboard.topVolunteers.map((v, i) => `
      <tr style="border-bottom: 1px solid #f1f5f9;">
        <td style="padding: 12px; font-weight: 700; color: ${i === 0 ? '#eab308' : '#64748b'};">#${i + 1}</td>
        <td style="padding: 12px;">
          <div style="font-weight: 700; color: #0f172a;">${escapeHtml(v.name)}</div>
          <div style="font-size: 0.78rem; color: #64748b;">${escapeHtml(v.organization || 'Volunteer')}</div>
        </td>
        <td style="padding: 12px; font-weight: 800; color: #0ea5e9;">${v.rescued_meals_count.toLocaleString()} rescued</td>
        <td style="padding: 12px; font-size: 0.85rem; color: #475569;">⭐ ${v.rating.toFixed(1)}</td>
      </tr>
    `).join('');
  }
}

// Render Emergency Ticker & Alerts
function renderAlerts() {
  const ticker = document.getElementById('global-alert-ticker');
  if (ticker && state.alerts.length > 0) {
    const text = state.alerts.map(a => `⚠️ ${a.title}: ${a.message}`).join('  ✦  ');
    ticker.textContent = text;
  }
}

// Render Aid Requests
function renderAidRequests() {
  const container = document.getElementById('aid-requests-list');
  if (!container) return;

  if (state.aidRequests.length === 0) {
    container.innerHTML = `<p style="color: #64748b; font-size: 0.9rem;">No active emergency aid requests.</p>`;
    return;
  }

  container.innerHTML = state.aidRequests.map(r => `
    <div style="background: #fff; border: 1px solid #fecaca; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: 700; color: #b91c1c; font-size: 0.85rem;">🚨 ${r.urgency.toUpperCase()} ASSISTANCE NEEDED</span>
        <span style="background: #fee2e2; color: #991b1b; font-size: 0.75rem; font-weight: 700; padding: 2px 6px; border-radius: 4px;">${r.servings_needed} Servings</span>
      </div>
      <h5 style="font-weight: 700; color: #1e293b; margin: 4px 0;">${escapeHtml(r.recipient_name)}</h5>
      <p style="font-size: 0.82rem; color: #475569;">${escapeHtml(r.notes || 'Direct community distribution request.')}</p>
    </div>
  `).join('');
}

// Modal Handlers & Actions
function initModalListeners() {
  // Post Donation Form Submit
  const donateForm = document.getElementById('form-post-donation');
  if (donateForm) {
    donateForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const user = state.userProfile[state.currentRole];

      const payload = {
        donor_id: user.id,
        donor_name: user.name,
        title: document.getElementById('donate-title').value,
        category: document.getElementById('donate-category').value,
        food_type: document.getElementById('donate-food-type').value,
        servings: parseInt(document.getElementById('donate-servings').value, 10),
        weight_kg: parseFloat(document.getElementById('donate-weight').value) || 0,
        pickup_address: document.getElementById('donate-address').value,
        expiry_time: new Date(Date.now() + parseFloat(document.getElementById('donate-expiry-hours').value) * 3600 * 1000).toISOString(),
        packaging_type: document.getElementById('donate-packaging').value,
        allergens: document.getElementById('donate-allergens').value,
        description: document.getElementById('donate-description').value,
        image_url: document.getElementById('donate-image-preset').value
      };

      try {
        const res = await fetch('/api/donations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error('Failed to create donation');
        const created = await res.json();

        closeModal('modal-post-donation');
        donateForm.reset();
        triggerToast('Donation Listed!', `Your donation of ${created.servings} meals is live on the rescue map!`, 'high');
      } catch (err) {
        alert(err.message);
      }
    });
  }

  // Aid Request Form Submit
  const aidForm = document.getElementById('form-aid-request');
  if (aidForm) {
    aidForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        recipient_id: state.userProfile.recipient.id,
        recipient_name: document.getElementById('aid-shelter-name').value,
        servings_needed: parseInt(document.getElementById('aid-servings-needed').value, 10),
        urgency: document.getElementById('aid-urgency').value,
        notes: document.getElementById('aid-notes').value
      };

      try {
        const res = await fetch('/api/aid-requests', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('Failed to submit aid request');
        closeModal('modal-aid-request');
        aidForm.reset();
        loadAidRequests();
        triggerToast('Aid Request Broadcasted', 'Nearby restaurants and donors have been alerted!', 'emergency');
      } catch (err) {
        alert(err.message);
      }
    });
  }

  // Filter Listeners
  const filterInputs = ['filter-search', 'filter-category', 'filter-food-type', 'filter-status'];
  filterInputs.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', renderDonationsList);
      el.addEventListener('change', renderDonationsList);
    }
  });
}

// Claim Donation Action
window.claimDonation = async function(donationId) {
  const user = state.userProfile[state.currentRole];
  const recipientName = user.role === 'recipient' ? user.name : 'Asha Child Hope Home & Orphanage';

  if (!confirm(`Claim this surplus food for ${recipientName}? A volunteer run will be scheduled immediately.`)) {
    return;
  }

  try {
    const res = await fetch(`/api/donations/${donationId}/claim`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        recipient_id: user.id,
        recipient_name: recipientName,
        notes: 'Priority dinner distribution'
      })
    });
    if (!res.ok) throw new Error('Failed to claim donation');
    const updated = await res.json();
    updateLocalDonation(updated);
    renderDonationsList();
    renderMapMarkers();
    renderDeliveriesSection();
  } catch (err) {
    alert(err.message);
  }
};

// Volunteer Assign Action
window.assignVolunteer = async function(donationId) {
  const user = state.userProfile[state.currentRole];
  const volName = user.role === 'volunteer' ? user.name : 'Kabir Das (Youth Chapter Runner)';

  if (!confirm(`Accept pickup and delivery run as volunteer ${volName}?`)) {
    return;
  }

  try {
    const res = await fetch(`/api/donations/${donationId}/assign-volunteer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        volunteer_id: user.id,
        volunteer_name: volName,
        proof_notes: 'Volunteer dispatch accepted via mobile console'
      })
    });
    if (!res.ok) throw new Error('Failed to accept delivery run');
    const updated = await res.json();
    updateLocalDonation(updated);
    renderDonationsList();
    renderMapMarkers();
    renderDeliveriesSection();
  } catch (err) {
    alert(err.message);
  }
};

// Verify Delivery Modal
let currentVerifyingDonationId = null;
window.openVerifyDeliveryModal = function(donationId, expectedCode) {
  currentVerifyingDonationId = donationId;
  const modal = document.getElementById('modal-verify-delivery');
  const codeHint = document.getElementById('verify-otp-hint');
  if (codeHint) {
    codeHint.textContent = expectedCode ? `[Recipient Handover OTP: ${expectedCode}]` : '';
  }
  if (modal) modal.classList.remove('hidden');
};

window.submitDeliveryVerification = async function() {
  if (!currentVerifyingDonationId) return;

  const otpInput = document.getElementById('verify-otp-input');
  const notesInput = document.getElementById('verify-notes-input');
  const otp = otpInput ? otpInput.value.trim() : '';

  try {
    const res = await fetch(`/api/donations/${currentVerifyingDonationId}/verify-delivery`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        verification_code: otp,
        proof_notes: notesInput ? notesInput.value : 'Safe handover confirmed'
      })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.message || 'Verification failed');
    }

    const updated = await res.json();
    updateLocalDonation(updated);
    closeModal('modal-verify-delivery');
    if (otpInput) otpInput.value = '';
    renderDonationsList();
    renderMapMarkers();
    renderDeliveriesSection();
    loadImpactMetrics();
    loadLeaderboard();
  } catch (err) {
    alert(err.message);
  }
};

// AI Food Safety Advisor Component
function initAiAdvisor() {
  const advisorForm = document.getElementById('advisor-calc-form');
  if (!advisorForm) return;

  advisorForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      category: document.getElementById('adv-category').value,
      food_type: document.getElementById('adv-food-type').value,
      prepared_hours_ago: parseFloat(document.getElementById('adv-hours-ago').value),
      storage_type: document.getElementById('adv-storage').value,
      ambient_temp_c: parseFloat(document.getElementById('adv-temp').value)
    };

    try {
      const res = await fetch('/api/ai-advisor/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error('Analysis failed');
      const data = await res.json();

      const resultBox = document.getElementById('advisor-results');
      if (resultBox) {
        resultBox.classList.remove('hidden');

        document.getElementById('adv-score-val').textContent = `${data.safety_score}/100`;
        document.getElementById('adv-hours-remaining').textContent = `${data.estimated_hours_remaining} Hours Safe`;
        
        const urgencyEl = document.getElementById('adv-urgency-badge');
        urgencyEl.textContent = data.urgency.toUpperCase();
        urgencyEl.className = `font-bold px-3 py-1 rounded text-xs ${data.urgency === 'emergency' ? 'bg-red-100 text-red-800' : (data.urgency === 'high' ? 'bg-amber-100 text-amber-800' : 'bg-green-100 text-green-800')}`;

        const guidelinesList = document.getElementById('adv-guidelines-list');
        guidelinesList.innerHTML = data.haccp_guidelines.map(g => `<li style="margin-bottom: 4px;">• ${escapeHtml(g)}</li>`).join('');
      }
    } catch (err) {
      alert(err.message);
    }
  });
}

// Modal Toggle Helpers
window.openModal = function(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('hidden');
};

window.closeModal = function(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('hidden');
};

window.openAidRequestModal = function(shelterName = '') {
  const nameInput = document.getElementById('aid-shelter-name');
  if (nameInput && shelterName) nameInput.value = shelterName;
  openModal('modal-aid-request');
};

window.triggerDatabaseReset = async function() {
  if (!confirm('Reset database to realistic default demo state?')) return;
  try {
    const res = await fetch('/api/seed', { method: 'POST' });
    if (res.ok) {
      await loadAllData();
      triggerToast('Database Reset', 'Sample data restored!', 'info');
    }
  } catch (err) {
    alert(err.message);
  }
};
