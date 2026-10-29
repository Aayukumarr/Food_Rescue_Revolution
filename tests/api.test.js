// tests/api.test.js - Comprehensive Automated Test Suite
const test = require('node:test');
const assert = require('node:assert/strict');
const { Readable } = require('node:stream');
const { EventEmitter } = require('node:events');
const { server, db } = require('../server.js');
const { seedDatabase } = require('../db.js');

// Mock request runner to invoke HTTP server directly without network socket bind
function callServer(method, path, bodyObj = null) {
  return new Promise((resolve) => {
    const bodyStr = bodyObj ? JSON.stringify(bodyObj) : null;
    let pushed = false;

    const req = new Readable({
      read() {
        if (!pushed) {
          if (bodyStr) this.push(bodyStr);
          this.push(null);
          pushed = true;
        }
      }
    });

    req.method = method;
    req.url = path;
    req.headers = {
      'content-type': 'application/json',
      'host': 'localhost:3000'
    };

    let responseData = '';
    const res = new EventEmitter();
    res.statusCode = 200;
    res.headers = {};

    res.writeHead = (status, headers) => {
      res.statusCode = status;
      res.headers = headers;
    };

    res.write = (chunk) => {
      responseData += chunk;
    };

    res.end = (chunk) => {
      if (chunk) responseData += chunk;
      try {
        const json = responseData ? JSON.parse(responseData) : null;
        resolve({ status: res.statusCode, data: json, text: responseData, headers: res.headers });
      } catch (e) {
        resolve({ status: res.statusCode, data: null, text: responseData, headers: res.headers });
      }
    };

    server.emit('request', req, res);
  });
}

test.before(() => {
  seedDatabase(db);
});

test('GET / should serve index.html with 200 OK', async () => {
  const res = await callServer('GET', '/');
  assert.equal(res.status, 200);
  assert.ok(res.text.includes('Food Rescue Revolution'));
  assert.equal(res.headers['Content-Type'], 'text/html; charset=utf-8');
});

test('GET /styles.css should serve CSS file', async () => {
  const res = await callServer('GET', '/styles.css');
  assert.equal(res.status, 200);
  assert.ok(res.text.includes('--primary'));
});

test('GET /app.js should serve client JavaScript', async () => {
  const res = await callServer('GET', '/app.js');
  assert.equal(res.status, 200);
  assert.ok(res.text.includes('initRoleSwitcher'));
});

test('GET /api/health should return online status', async () => {
  const res = await callServer('GET', '/api/health');
  assert.equal(res.status, 200);
  assert.equal(res.data.status, 'online');
  assert.equal(res.data.name, 'Food Rescue Revolution API');
});

test('GET /api/donations should return list of seeded donations', async () => {
  const res = await callServer('GET', '/api/donations');
  assert.equal(res.status, 200);
  assert.ok(Array.isArray(res.data));
  assert.ok(res.data.length >= 4);
  const item = res.data[0];
  assert.ok(item.title);
  assert.ok(item.servings > 0);
  assert.ok(item.pickup_address);
});

test('GET /api/impact should return carbon and meal statistics', async () => {
  const res = await callServer('GET', '/api/impact');
  assert.equal(res.status, 200);
  assert.ok(res.data.total_meals > 0);
  assert.ok(res.data.co2_avoided_kg > 0);
  assert.ok(res.data.water_saved_liters > 0);
  assert.ok(Array.isArray(res.data.categoryBreakdown));
});

test('GET /api/leaderboard should return top donors and volunteers', async () => {
  const res = await callServer('GET', '/api/leaderboard');
  assert.equal(res.status, 200);
  assert.ok(Array.isArray(res.data.topDonors));
  assert.ok(Array.isArray(res.data.topVolunteers));
  assert.ok(res.data.topDonors.length > 0);
});

test('Complete Rescue Lifecycle: Create -> Claim -> Assign Volunteer -> Verify Delivery', async () => {
  // 1. Create Donation
  const postRes = await callServer('POST', '/api/donations', {
    title: 'Automated Test Surplus Biryani',
    category: 'cooked_meals',
    food_type: 'veg',
    servings: 60,
    weight_kg: 24,
    pickup_address: 'Sector 18 Grand Kitchen, Noida',
    donor_name: 'Imperial Feast Caterers'
  });
  assert.equal(postRes.status, 201);
  const donation = postRes.data;
  assert.ok(donation.id);
  assert.equal(donation.status, 'available');
  assert.ok(donation.verification_code);

  // 2. Claim Donation as NGO
  const claimRes = await callServer('POST', `/api/donations/${donation.id}/claim`, {
    recipient_id: 'usr-rec-1',
    recipient_name: 'Hope Children Shelter',
    notes: 'Dinner distribution for 60 children'
  });
  assert.equal(claimRes.status, 200);
  assert.equal(claimRes.data.status, 'claimed');
  assert.equal(claimRes.data.recipient_name, 'Hope Children Shelter');

  // 3. Assign Volunteer
  const volRes = await callServer('POST', `/api/donations/${donation.id}/assign-volunteer`, {
    volunteer_id: 'usr-vol-1',
    volunteer_name: 'Kabir Das'
  });
  assert.equal(volRes.status, 200);
  assert.equal(volRes.data.status, 'in_transit');
  assert.equal(volRes.data.volunteer_name, 'Kabir Das');

  // 4. Verify Delivery with Correct OTP
  const deliverRes = await callServer('POST', `/api/donations/${donation.id}/verify-delivery`, {
    verification_code: donation.verification_code,
    proof_notes: 'Delivered in insulated food boxes safely'
  });
  assert.equal(deliverRes.status, 200);
  assert.equal(deliverRes.data.status, 'delivered');
});

test('POST /api/ai-advisor/analyze calculates shelf life and urgency', async () => {
  const res = await callServer('POST', '/api/ai-advisor/analyze', {
    category: 'cooked_meals',
    food_type: 'non_veg',
    prepared_hours_ago: 2.5,
    storage_type: 'room_temperature',
    ambient_temp_c: 32
  });
  assert.equal(res.status, 200);
  assert.ok(res.data.safe_shelf_life_hours > 0);
  assert.ok(res.data.estimated_hours_remaining !== undefined);
  assert.ok(['emergency', 'high', 'normal'].includes(res.data.urgency));
  assert.ok(Array.isArray(res.data.haccp_guidelines));
});

test('POST & GET /api/aid-requests handles shelter requests', async () => {
  const postRes = await callServer('POST', '/api/aid-requests', {
    recipient_name: 'Prerna Community Kitchen',
    servings_needed: 75,
    urgency: 'immediate',
    notes: 'Evening outreach distribution'
  });
  assert.equal(postRes.status, 201);

  const getRes = await callServer('GET', '/api/aid-requests');
  assert.equal(getRes.status, 200);
  assert.ok(getRes.data.length > 0);
});
