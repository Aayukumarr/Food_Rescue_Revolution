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

// Portal Authentication Passwords (configurable via env vars)
let ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';
let DONOR_PASSWORD = process.env.DONOR_PASSWORD || 'donor123';
let NGO_PASSWORD = process.env.NGO_PASSWORD || 'ngo123';

// Active OTP store for Phone Number Authentication (phone -> { otp, role, expiresAt })
const activeOtps = new Map();

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

    // POST /api/auth/send-otp (Send Mobile OTP)
    if (pathname === '/api/auth/send-otp' && req.method === 'POST') {
      const body = await parseJsonBody(req);
      const rawPhone = (body.phone || '').trim();
      const role = body.role || 'donor';

      if (!rawPhone || rawPhone.replace(/\D/g, '').length < 6) {
        return sendError(res, 400, 'Please enter a valid phone number (at least 6 digits).');
      }

      const cleanPhone = rawPhone.replace(/\D/g, '');
      const otp = '4821';
      activeOtps.set(cleanPhone, { otp, role, expiresAt: Date.now() + 10 * 60 * 1000 });

      broadcastEvent('sms_otp', {
        phone: rawPhone,
        otp,
        role,
        message: `[Food Rescue Security] Your login OTP is: ${otp}. Valid for 10 minutes.`
      });

      return sendJson(res, 200, {
        success: true,
        message: `OTP sent successfully to ${rawPhone}`,
        phone: rawPhone,
        demo_otp: otp,
        expiresInSeconds: 600
      });
    }

    // POST /api/auth/verify-otp (Verify Mobile OTP)
    if (pathname === '/api/auth/verify-otp' && req.method === 'POST') {
      const body = await parseJsonBody(req);
      const rawPhone = (body.phone || '').trim();
      const enteredOtp = (body.otp || '').trim();
      const role = body.role || 'donor';

      const cleanPhone = rawPhone.replace(/\D/g, '');
      const record = activeOtps.get(cleanPhone);

      const isValid = (record && record.otp === enteredOtp && Date.now() <= record.expiresAt) ||
                      enteredOtp === '4821' || enteredOtp === '1234';

      if (!isValid) {
        return sendError(res, 401, 'Invalid or expired OTP. Please use demo OTP: 4821');
      }

      activeOtps.delete(cleanPhone);
      const token = crypto.createHash('sha256').update(enteredOtp + `_salt_${role}_2026`).digest('hex');
      const userProfiles = {
        donor: { id: 'usr-donor-1', name: 'Chef Rajesh Sharma', org: 'The Grand Heritage Banquet & Hotel', role: 'donor', phone: rawPhone },
        ngo: { id: 'usr-rec-1', name: 'Sister Mary Teresa', org: 'Asha Child Hope Home & Orphanage', role: 'recipient', phone: rawPhone },
        admin: { id: 'usr-admin-1', name: 'Antigravity Coordinator', org: 'Food Rescue Revolution HQ', role: 'admin', phone: rawPhone }
      };

      return sendJson(res, 200, {
        success: true,
        authenticated: true,
        role,
        token,
        auth_method: 'phone_otp',
        user: userProfiles[role] || { role, phone: rawPhone },
        message: `${role.toUpperCase()} authorized via Phone OTP successfully.`
      });
    }

    // POST /api/admin/login (Admin Password or OTP Authentication)
    if (pathname === '/api/admin/login' && req.method === 'POST') {
      const body = await parseJsonBody(req);
      if (body.otp) {
        if (body.otp === '4821' || body.otp === '1234') {
          const token = crypto.createHash('sha256').update('admin_otp_' + Date.now()).digest('hex');
          return sendJson(res, 200, { success: true, authenticated: true, token, user: { name: 'Admin HQ', role: 'admin' }, message: 'Admin authorized via OTP.' });
        }
        return sendError(res, 401, 'Invalid OTP. Demo OTP is: 4821');
      }
      if (body.password === ADMIN_PASSWORD) {
        const token = crypto.createHash('sha256').update(ADMIN_PASSWORD + '_salt_rescue_2026').digest('hex');
        return sendJson(res, 200, {
          success: true,
          authenticated: true,
          token,
          user: { name: 'Admin HQ', role: 'admin' },
          message: 'Admin authorization successful.'
        });
      }
      return sendError(res, 401, 'Incorrect admin password. Default password is: admin123');
    }

    // POST /api/admin/change-password
    if (pathname === '/api/admin/change-password' && req.method === 'POST') {
      const body = await parseJsonBody(req);
      if (!body.old_password || body.old_password !== ADMIN_PASSWORD) {
        return sendError(res, 401, 'Current password verification failed.');
      }
      if (!body.new_password || body.new_password.length < 4) {
        return sendError(res, 400, 'New password must be at least 4 characters long.');
      }
      ADMIN_PASSWORD = body.new_password;
      return sendJson(res, 200, { success: true, message: 'Admin password changed successfully.' });
    }

    // POST /api/donor/login (Donor Password or OTP Authentication)
    if (pathname === '/api/donor/login' && req.method === 'POST') {
      const body = await parseJsonBody(req);
      if (body.otp) {
        if (body.otp === '4821' || body.otp === '1234') {
          const token = crypto.createHash('sha256').update('donor_otp_' + Date.now()).digest('hex');
          return sendJson(res, 200, {
            success: true,
            authenticated: true,
            role: 'donor',
            token,
            user: { id: 'usr-donor-1', name: 'Chef Rajesh Sharma', org: 'The Grand Heritage Banquet & Hotel', role: 'donor' },
            message: 'Donor authorized via OTP.'
          });
        }
        return sendError(res, 401, 'Invalid OTP. Demo OTP is: 4821');
      }
      if (body.password === DONOR_PASSWORD) {
        const token = crypto.createHash('sha256').update(DONOR_PASSWORD + '_salt_donor_2026').digest('hex');
        return sendJson(res, 200, {
          success: true,
          authenticated: true,
          role: 'donor',
          token,
          user: { id: 'usr-donor-1', name: 'Chef Rajesh Sharma', org: 'The Grand Heritage Banquet & Hotel', role: 'donor' },
          message: 'Donor authorization successful.'
        });
      }
      return sendError(res, 401, 'Incorrect donor password. Default password is: donor123');
    }

    // POST /api/donor/change-password
    if (pathname === '/api/donor/change-password' && req.method === 'POST') {
      const body = await parseJsonBody(req);
      if (!body.old_password || body.old_password !== DONOR_PASSWORD) {
        return sendError(res, 401, 'Current password verification failed.');
      }
      if (!body.new_password || body.new_password.length < 4) {
        return sendError(res, 400, 'New password must be at least 4 characters long.');
      }
      DONOR_PASSWORD = body.new_password;
      return sendJson(res, 200, { success: true, message: 'Donor password changed successfully.' });
    }

    // POST /api/ngo/login (NGO & Shelter Password or OTP Authentication)
    if (pathname === '/api/ngo/login' && req.method === 'POST') {
      const body = await parseJsonBody(req);
      if (body.otp) {
        if (body.otp === '4821' || body.otp === '1234') {
          const token = crypto.createHash('sha256').update('ngo_otp_' + Date.now()).digest('hex');
          return sendJson(res, 200, {
            success: true,
            authenticated: true,
            role: 'ngo',
            token,
            user: { id: 'usr-rec-1', name: 'Sister Mary Teresa', org: 'Asha Child Hope Home & Orphanage', role: 'recipient' },
            message: 'NGO authorized via OTP.'
          });
        }
        return sendError(res, 401, 'Invalid OTP. Demo OTP is: 4821');
      }
      if (body.password === NGO_PASSWORD) {
        const token = crypto.createHash('sha256').update(NGO_PASSWORD + '_salt_ngo_2026').digest('hex');
        return sendJson(res, 200, {
          success: true,
          authenticated: true,
          role: 'ngo',
          token,
          user: { id: 'usr-rec-1', name: 'Sister Mary Teresa', org: 'Asha Child Hope Home & Orphanage', role: 'recipient' },
          message: 'NGO authorization successful.'
        });
      }
      return sendError(res, 401, 'Incorrect NGO password. Default password is: ngo123');
    }

    // POST /api/ngo/change-password
    if (pathname === '/api/ngo/change-password' && req.method === 'POST') {
      const body = await parseJsonBody(req);
      if (!body.old_password || body.old_password !== NGO_PASSWORD) {
        return sendError(res, 401, 'Current password verification failed.');
      }
      if (!body.new_password || body.new_password.length < 4) {
        return sendError(res, 400, 'New password must be at least 4 characters long.');
      }
      NGO_PASSWORD = body.new_password;
      return sendJson(res, 200, { success: true, message: 'NGO password changed successfully.' });
    }

    // POST /api/auth/login (Unified Role Auth)
    if (pathname === '/api/auth/login' && req.method === 'POST') {
      const body = await parseJsonBody(req);
      const role = body.role || 'donor';
      let expectedPwd = role === 'admin' ? ADMIN_PASSWORD : (role === 'ngo' ? NGO_PASSWORD : DONOR_PASSWORD);
      let defaultPwd = role === 'admin' ? 'admin123' : (role === 'ngo' ? 'ngo123' : 'donor123');
      if (body.password === expectedPwd) {
        const token = crypto.createHash('sha256').update(expectedPwd + `_salt_${role}_2026`).digest('hex');
        return sendJson(res, 200, {
          success: true,
          authenticated: true,
          role,
          token,
          message: `${role.toUpperCase()} authorization successful.`
        });
      }
      return sendError(res, 401, `Incorrect ${role} password. Default is: ${defaultPwd}`);
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

    // DELETE /api/donations/:id (Admin or Donor removes listing)
    if (donationIdMatch && req.method === 'DELETE') {
      const id = donationIdMatch[1];
      const donation = db.getDonationById(id);
      if (!donation) return sendError(res, 404, 'Donation not found');
      db.deleteDonation(id);
      broadcastEvent('donation_deleted', { id });
      return sendJson(res, 200, { success: true, message: 'Donation deleted successfully.' });
    }

    // GET /api/donors/:id/stats
    const donorStatsMatch = pathname.match(/^\/api\/donors\/([a-zA-Z0-9_-]+)\/stats$/);
    if (donorStatsMatch && req.method === 'GET') {
      const stats = db.getDonorStats(donorStatsMatch[1]);
      return sendJson(res, 200, stats);
    }

    // GET /api/ngos/:id/stats
    const ngoStatsMatch = pathname.match(/^\/api\/ngos\/([a-zA-Z0-9_-]+)\/stats$/);
    if (ngoStatsMatch && req.method === 'GET') {
      const stats = db.getNgoStats(ngoStatsMatch[1]);
      return sendJson(res, 200, stats);
    }

    // PATCH /api/users/:id (Admin verify or update badge)
    const userPatchMatch = pathname.match(/^\/api\/users\/([a-zA-Z0-9_-]+)$/);
    if (userPatchMatch && req.method === 'PATCH') {
      const body = await parseJsonBody(req);
      const updated = db.updateUser(userPatchMatch[1], body);
      if (!updated) return sendError(res, 404, 'User not found');
      broadcastEvent('user_updated', updated);
      return sendJson(res, 200, updated);
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
        'Cache-Control': 'no-cache, no-store, must-revalidate'
      });

      fs.createReadStream(filePath).pipe(res);
    });

  } catch (err) {
    console.error('Server error:', err);
    sendError(res, 500, 'Internal Server Error: ' + err.message);
  }
});

// Start Server with automatic port fallback if 3000 is occupied
if (require.main === module) {
  let currentPort = Number(PORT);
  const os = require('node:os');

  function getLocalNetworkIp() {
    try {
      const nets = os.networkInterfaces();
      for (const name of Object.keys(nets)) {
        for (const net of nets[name]) {
          if (net.family === 'IPv4' && !net.internal) {
            return net.address;
          }
        }
      }
    } catch (e) {}
    return null;
  }

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.warn(`⚠️ Port ${currentPort} is already in use. Retrying on port ${currentPort + 1}...`);
      currentPort += 1;
      server.listen(currentPort, '0.0.0.0');
    } else {
      console.error('Server failed to start:', err);
    }
  });

  server.listen(currentPort, '0.0.0.0', () => {
    const localUrl = `http://localhost:${currentPort}`;
    const networkIp = getLocalNetworkIp();
    const networkUrl = networkIp ? `http://${networkIp}:${currentPort}` : null;

    console.log(`\n======================================================`);
    console.log(`🌍 Food Rescue Revolution Platform`);
    console.log(`💻 Local (Aapke laptop ke liye):   ${localUrl}`);
    if (networkUrl) {
      console.log(`📱 Same Wi-Fi / Hotspot Share Link: ${networkUrl}`);
    }
    console.log(`🌐 Public Link (Kahin bhi share karne ke liye):`);
    console.log(`   Terminal me run karein: npx localtunnel --port ${currentPort}`);
    console.log(`📊 API Health:                     ${localUrl}/api/health`);
    console.log(`======================================================\n`);

    // Auto-open browser in user's default browser (Mac: open, Windows: start, Linux: xdg-open)
    if (process.env.AUTO_OPEN !== 'false') {
      const { exec } = require('node:child_process');
      const openCmd = process.platform === 'darwin' ? `open ${localUrl}` : (process.platform === 'win32' ? `start ${localUrl}` : `xdg-open ${localUrl}`);
      exec(openCmd, (err) => {
        // Silently ignore if running in headless or sandbox environment
      });
    }
  });
}

module.exports = { server, db, broadcastEvent };

