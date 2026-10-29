// server.js - Fast, Zero-Dependency Full-Stack Node Server for Food Rescue Revolution
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const url = require('node:url');
const crypto = require('node:crypto');
const { DatabaseManager } = require('./db.js');

const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.join(__dirname, 'public');
const db = new DatabaseManager();

// Server-Sent Events (SSE) Client Subscribers
const sseClients = new Set();

function broadcastEvent(type, data) {
  const payload = `event: ${type}\ndata: ${JSON.stringify(data)}\n\n`;
  for (const client of sseClients) {
    try {
      client.write(payload);
    } catch (err) {
      sseClients.delete(client);
    }
  }
}

// MIME Types Map
const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

// Utility to parse JSON request body
function parseJsonBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk;
      if (body.length > 5 * 1024 * 1024) { // 5MB limit
        reject(new Error('Payload too large'));
      }
    });
    req.on('end', () => {
      if (!body.trim()) return resolve({});
      try {
        resolve(JSON.parse(body));
      } catch (err) {
        reject(new Error('Invalid JSON format: ' + err.message));
      }
    });
    req.on('error', reject);
  });
}

// JSON Response Helper
function sendJson(res, statusCode, data) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PATCH, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
  });
  res.end(JSON.stringify(data));
}

// Error Response Helper
function sendError(res, statusCode, message) {
  sendJson(res, statusCode, { error: true, message });
}

// AI Food Safety & Urgency Advisor Rule-based Engine
function analyzeFoodSafety({ category, food_type, prepared_hours_ago, storage_type, ambient_temp_c = 28 }) {
  let safe_shelf_life_hours = 6;
  const guidelines = [];
  let urgency = 'medium';
  let safety_score = 90;

  if (category === 'cooked_meals') {
    if (food_type === 'non_veg') {
      safe_shelf_life_hours = 4;
      guidelines.push('High protein perishable. Must maintain internal temperature above 65°C or chill under 4°C.');
    } else {
      safe_shelf_life_hours = 5.5;
      guidelines.push('Hot-cooked vegetarian surplus. Preserve in insulated steam pans or insulated food carriers.');
    }
  } else if (category === 'bakery') {
    safe_shelf_life_hours = 36;
    guidelines.push('Dry baked goods. Keep sealed away from humidity; inspect for mold or physical damage.');
  } else if (category === 'fresh_produce') {
    safe_shelf_life_hours = 48;
    guidelines.push('Wash produce thoroughly before serving. Check for transit bruising.');
  } else if (category === 'dairy') {
    safe_shelf_life_hours = 4;
    guidelines.push('Strict cold chain essential. Keep under 4°C at all times.');
  } else {
    safe_shelf_life_hours = 24;
    guidelines.push('Packaged goods: Check tamper-evident seals and expiration label.');
  }

  // Adjust for ambient summer temperature
  if (ambient_temp_c > 30 && storage_type !== 'refrigerated') {
    safe_shelf_life_hours = Math.max(2, safe_shelf_life_hours * 0.75);
    guidelines.push('High ambient room temperature accelerates bacterial growth: Rapid dispatch recommended.');
    safety_score -= 15;
  }

  if (storage_type === 'refrigerated') {
    safe_shelf_life_hours *= 2.5;
    safety_score += 10;
  }

  const hoursRemaining = Math.max(0, safe_shelf_life_hours - (prepared_hours_ago || 0));

  if (hoursRemaining <= 2.5) {
    urgency = 'emergency';
  } else if (hoursRemaining <= 5) {
    urgency = 'high';
  } else {
    urgency = 'normal';
  }

  return {
    safe_shelf_life_hours: Number(safe_shelf_life_hours.toFixed(1)),
    estimated_hours_remaining: Number(hoursRemaining.toFixed(1)),
    urgency,
    safety_score: Math.min(100, Math.max(20, Math.round(safety_score))),
    is_safe_to_distribute: hoursRemaining > 0.5,
    haccp_guidelines: guidelines,
    dispatch_priority: urgency === 'emergency' ? 'RED ALERT: Immediate volunteer dispatch required' : 'NORMAL: Standard pickup schedule'
  };
}

// Request Router
const server = http.createServer(async (req, res) => {
  // CORS Preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PATCH, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    });
    return res.end();
  }

  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const query = parsedUrl.query;

  try {
    // 1. SSE Stream Route
    if (pathname === '/api/events' && req.method === 'GET') {
      res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*'
      });
      res.write(`event: connected\ndata: ${JSON.stringify({ status: 'connected', time: new Date().toISOString() })}\n\n`);
      sseClients.add(res);

      req.on('close', () => {
        sseClients.delete(res);
      });
      return;
    }

    // 2. REST API Routes
    if (pathname === '/api/health' && req.method === 'GET') {
      return sendJson(res, 200, {
        status: 'online',
        name: 'Food Rescue Revolution API',
        version: '1.0.0',
        timestamp: new Date().toISOString()
      });
    }

    // GET /api/donations
    if (pathname === '/api/donations' && req.method === 'GET') {
      const donations = db.getAllDonations(query);
      return sendJson(res, 200, donations);
    }

    // POST /api/donations
    if (pathname === '/api/donations' && req.method === 'POST') {
      const body = await parseJsonBody(req);
      if (!body.title || !body.servings || !body.pickup_address) {
        return sendError(res, 400, 'Title, servings, and pickup address are required.');
      }

      const id = 'don-' + Date.now().toString().slice(-6) + '-' + Math.floor(Math.random() * 1000);
      const donationData = {
        id,
        donor_id: body.donor_id || 'usr-donor-1',
        donor_name: body.donor_name || 'Anonymous Generous Donor',
        title: body.title,
        description: body.description || '',
        category: body.category || 'cooked_meals',
        food_type: body.food_type || 'veg',
        servings: parseInt(body.servings, 10),
        weight_kg: parseFloat(body.weight_kg) || (parseInt(body.servings, 10) * 0.4),
        prepared_at: body.prepared_at || new Date().toISOString(),
        expiry_time: body.expiry_time || new Date(Date.now() + 4 * 3600 * 1000).toISOString(),
        pickup_address: body.pickup_address,
        lat: parseFloat(body.lat) || (28.6139 + (Math.random() - 0.5) * 0.08),
        lng: parseFloat(body.lng) || (77.2090 + (Math.random() - 0.5) * 0.08),
        storage_instructions: body.storage_instructions || 'Keep in clean, covered container',
        packaging_type: body.packaging_type || 'Food-safe container',
        allergens: body.allergens || 'None reported',
        status: 'available',
        image_url: body.image_url || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80'
      };

      const created = db.createDonation(donationData);

      // Check if expiration is tight (<3 hours) -> generate emergency alert
      const expiryDiffHours = (new Date(created.expiry_time) - Date.now()) / (3600 * 1000);
      const alert = {
        id: 'alt-' + Date.now(),
        title: expiryDiffHours <= 3 ? `🚨 URGENT Surplus Alert: ${created.title}` : `🍲 New Food Donation: ${created.title}`,
        message: `${created.servings} servings available at ${created.pickup_address}. Rescued by ${created.donor_name}.`,
        urgency: expiryDiffHours <= 3 ? 'emergency' : 'info',
        donation_id: created.id
      };
      db.createAlert(alert);

      // Real-time broadcast
      broadcastEvent('new_donation', created);
      broadcastEvent('new_alert', alert);

      return sendJson(res, 201, created);
    }

    // GET /api/donations/:id
    const donationIdMatch = pathname.match(/^\/api\/donations\/([a-zA-Z0-9_-]+)$/);
    if (donationIdMatch && req.method === 'GET') {
      const donation = db.getDonationById(donationIdMatch[1]);
      if (!donation) return sendError(res, 404, 'Donation not found');
      return sendJson(res, 200, donation);
    }

    // POST /api/donations/:id/claim (Recipient / NGO claims donation)
    const claimMatch = pathname.match(/^\/api\/donations\/([a-zA-Z0-9_-]+)\/claim$/);
    if (claimMatch && req.method === 'POST') {
      const id = claimMatch[1];
      const body = await parseJsonBody(req);
      const donation = db.getDonationById(id);

      if (!donation) return sendError(res, 404, 'Donation not found');
      if (donation.status !== 'available') {
        return sendError(res, 400, `Donation is already ${donation.status}`);
      }

      const updated = db.updateDonationStatus(id, 'claimed', {
        recipient_id: body.recipient_id || 'usr-rec-1',
        recipient_name: body.recipient_name || 'Asha Child Hope Home & Orphanage',
        claim_notes: body.notes || 'Claimed by registered NGO shelter'
      });

      const alert = {
        id: 'alt-' + Date.now(),
        title: `✅ Donation Claimed: ${donation.title}`,
        message: `${updated.recipient_name} has claimed ${updated.servings} servings. Ready for volunteer pickup!`,
        urgency: 'high',
        donation_id: id
      };
      db.createAlert(alert);

      broadcastEvent('donation_claimed', updated);
      broadcastEvent('new_alert', alert);

      return sendJson(res, 200, updated);
    }

    // POST /api/donations/:id/assign-volunteer (Volunteer claims pickup task)
    const volunteerMatch = pathname.match(/^\/api\/donations\/([a-zA-Z0-9_-]+)\/assign-volunteer$/);
    if (volunteerMatch && req.method === 'POST') {
      const id = volunteerMatch[1];
      const body = await parseJsonBody(req);
      const donation = db.getDonationById(id);

      if (!donation) return sendError(res, 404, 'Donation not found');

      const volunteerId = body.volunteer_id || 'usr-vol-1';
      const volunteerName = body.volunteer_name || 'Kabir Das';

      const updated = db.updateDonationStatus(id, 'in_transit', {
        volunteer_id: volunteerId,
        volunteer_name: volunteerName
      });

      db.createDelivery({
        id: 'del-' + Date.now(),
        donation_id: id,
        volunteer_id: volunteerId,
        volunteer_name: volunteerName,
        recipient_id: donation.recipient_id || 'usr-rec-1',
        recipient_name: donation.recipient_name || 'Partner Shelter',
        status: 'picked_up',
        picked_up_at: new Date().toISOString(),
        proof_notes: body.proof_notes || 'Volunteer assigned and in transit'
      });

      broadcastEvent('volunteer_assigned', updated);
      return sendJson(res, 200, updated);
    }

    // POST /api/donations/:id/verify-delivery (Complete rescue with OTP verification)
    const verifyMatch = pathname.match(/^\/api\/donations\/([a-zA-Z0-9_-]+)\/verify-delivery$/);
    if (verifyMatch && req.method === 'POST') {
      const id = verifyMatch[1];
      const body = await parseJsonBody(req);
      const donation = db.getDonationById(id);

      if (!donation) return sendError(res, 404, 'Donation not found');

      // Verify OTP code if provided
      if (body.verification_code && body.verification_code !== donation.verification_code) {
        return sendError(res, 400, 'Invalid Verification Code. Please verify with recipient.');
      }

      const updated = db.updateDonationStatus(id, 'delivered');
      db.updateDeliveryStatus(id, 'delivered', body.proof_notes || 'Delivered securely to recipient facility.');

      const alert = {
        id: 'alt-' + Date.now(),
        title: `🎉 Food Rescued Successfully!`,
        message: `${donation.servings} meals (${donation.weight_kg} kg) safely delivered to ${donation.recipient_name || 'shelter'}. Zero food waste achieved!`,
        urgency: 'info',
        donation_id: id
      };
      db.createAlert(alert);

      broadcastEvent('donation_delivered', updated);
      broadcastEvent('new_alert', alert);

      return sendJson(res, 200, updated);
    }

    // GET /api/impact (Real-time carbon & meals metrics)
    if (pathname === '/api/impact' && req.method === 'GET') {
      const impact = db.getImpactMetrics();
      return sendJson(res, 200, impact);
    }

    // GET /api/leaderboard
    if (pathname === '/api/leaderboard' && req.method === 'GET') {
      const leaderboard = db.getLeaderboard();
      return sendJson(res, 200, leaderboard);
    }

    // GET /api/users
    if (pathname === '/api/users' && req.method === 'GET') {
      if (query.role) {
        return sendJson(res, 200, db.getUsersByRole(query.role));
      }
      return sendJson(res, 200, db.getAllUsers());
    }

    // POST /api/users
    if (pathname === '/api/users' && req.method === 'POST') {
      const body = await parseJsonBody(req);
      if (!body.name || !body.role) {
        return sendError(res, 400, 'Name and role are required');
      }
      const newUser = {
        id: 'usr-' + Date.now().toString().slice(-6),
        name: body.name,
        role: body.role,
        organization: body.organization || '',
        phone: body.phone || '',
        email: body.email || '',
        address: body.address || '',
        lat: parseFloat(body.lat) || 28.6139,
        lng: parseFloat(body.lng) || 77.2090,
        badge: body.role === 'donor' ? 'Zero-Waste Champion 🌱' : (body.role === 'volunteer' ? 'Rescue Runner 🏃' : 'Community Partner 🤝')
      };
      const created = db.createUser(newUser);
      return sendJson(res, 201, created);
    }

    // GET /api/alerts
    if (pathname === '/api/alerts' && req.method === 'GET') {
      const limit = parseInt(query.limit, 10) || 10;
      return sendJson(res, 200, db.getRecentAlerts(limit));
    }

    // POST /api/alerts (Broadcast urgent emergency SOS)
    if (pathname === '/api/alerts' && req.method === 'POST') {
      const body = await parseJsonBody(req);
      const alert = {
        id: 'alt-' + Date.now(),
        title: body.title || '🚨 Community Emergency Alert',
        message: body.message || 'Urgent food pickup assistance requested.',
        urgency: body.urgency || 'emergency',
        donation_id: body.donation_id || null
      };
      db.createAlert(alert);
      broadcastEvent('new_alert', alert);
      return sendJson(res, 201, alert);
    }

    // GET /api/aid-requests
    if (pathname === '/api/aid-requests' && req.method === 'GET') {
      return sendJson(res, 200, db.getAllAidRequests());
    }

    // POST /api/aid-requests
    if (pathname === '/api/aid-requests' && req.method === 'POST') {
      const body = await parseJsonBody(req);
      if (!body.servings_needed) {
        return sendError(res, 400, 'Servings needed is required');
      }
      const reqData = {
        id: 'req-' + Date.now(),
        recipient_id: body.recipient_id || 'usr-rec-1',
        recipient_name: body.recipient_name || 'Local Community Center',
        servings_needed: parseInt(body.servings_needed, 10),
        urgency: body.urgency || 'today',
        notes: body.notes || ''
      };
      db.createAidRequest(reqData);
      broadcastEvent('new_aid_request', reqData);
      return sendJson(res, 201, reqData);
    }

    // POST /api/ai-advisor/analyze (AI Food Safety & Surplus Redistribution Advisor)
    if (pathname === '/api/ai-advisor/analyze' && req.method === 'POST') {
      const body = await parseJsonBody(req);
      const analysis = analyzeFoodSafety({
        category: body.category || 'cooked_meals',
        food_type: body.food_type || 'veg',
        prepared_hours_ago: parseFloat(body.prepared_hours_ago) || 1.5,
        storage_type: body.storage_type || 'room_temperature',
        ambient_temp_c: parseFloat(body.ambient_temp_c) || 28
      });
      return sendJson(res, 200, analysis);
    }

    // POST /api/seed (Reseed database)
    if (pathname === '/api/seed' && req.method === 'POST') {
      const { seedDatabase } = require('./db.js');
      seedDatabase(db);
      broadcastEvent('database_reset', { message: 'Database reset to default seed state' });
      return sendJson(res, 200, { success: true, message: 'Database reseeded successfully.' });
    }

    // 3. Static File Server (serves public directory)
    let safePath = path.normalize(pathname).replace(/^(\.\.[\/\\])+/, '');
    if (safePath === '/' || safePath === '') {
      safePath = '/index.html';
    }

    const filePath = path.join(PUBLIC_DIR, safePath);

    // Prevent directory traversal
    if (!filePath.startsWith(PUBLIC_DIR)) {
      return sendError(res, 403, 'Forbidden access');
    }

    fs.stat(filePath, (err, stats) => {
      if (err || !stats.isFile()) {
        // Fallback to index.html for Single Page Application navigation
        const fallbackIndex = path.join(PUBLIC_DIR, 'index.html');
        fs.readFile(fallbackIndex, (fbErr, content) => {
          if (fbErr) {
            return sendError(res, 404, 'Not Found');
          }
          res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
          res.end(content);
        });
        return;
      }

      const ext = path.extname(filePath).toLowerCase();
      const contentType = MIME_TYPES[ext] || 'application/octet-stream';

      res.writeHead(200, {
        'Content-Type': contentType,
        'Cache-Control': ext === '.html' ? 'no-cache' : 'public, max-age=3600'
      });

      fs.createReadStream(filePath).pipe(res);
    });

  } catch (err) {
    console.error('Server error:', err);
    sendError(res, 500, 'Internal Server Error: ' + err.message);
  }
});

// Start Server
if (require.main === module) {
  server.listen(PORT, () => {
    console.log(`\n======================================================`);
    console.log(`🌍 Food Rescue Revolution Platform`);
    console.log(`🚀 Server running at: http://localhost:${PORT}`);
    console.log(`📊 API Health:       http://localhost:${PORT}/api/health`);
    console.log(`📦 SSE Live Stream:  http://localhost:${PORT}/api/events`);
    console.log(`======================================================\n`);
  });
}

module.exports = { server, db, broadcastEvent };
