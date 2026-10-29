// db.js - SQLite Database Manager for Food Rescue Revolution
const { DatabaseSync } = require('node:sqlite');
const path = require('node:path');
const fs = require('node:fs');

const DB_PATH = path.join(__dirname, 'food_rescue.db');

class DatabaseManager {
  constructor(dbPath = DB_PATH) {
    this.db = new DatabaseSync(dbPath);
    this.initTables();
  }

  initTables() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        role TEXT NOT NULL, -- donor, recipient, volunteer, admin
        organization TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        lat REAL,
        lng REAL,
        badge TEXT,
        rating REAL DEFAULT 5.0,
        rescued_meals_count INTEGER DEFAULT 0,
        created_at TEXT
      );

      CREATE TABLE IF NOT EXISTS donations (
        id TEXT PRIMARY KEY,
        donor_id TEXT NOT NULL,
        donor_name TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT NOT NULL, -- cooked_meals, bakery, fresh_produce, dairy, packaged
        food_type TEXT NOT NULL, -- veg, non_veg, vegan
        servings INTEGER NOT NULL,
        weight_kg REAL NOT NULL,
        prepared_at TEXT,
        expiry_time TEXT NOT NULL,
        pickup_address TEXT NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        storage_instructions TEXT,
        packaging_type TEXT,
        allergens TEXT,
        status TEXT NOT NULL DEFAULT 'available', -- available, claimed, in_transit, delivered, expired
        recipient_id TEXT,
        recipient_name TEXT,
        volunteer_id TEXT,
        volunteer_name TEXT,
        claim_notes TEXT,
        verification_code TEXT,
        image_url TEXT,
        created_at TEXT
      );

      CREATE TABLE IF NOT EXISTS deliveries (
        id TEXT PRIMARY KEY,
        donation_id TEXT NOT NULL,
        volunteer_id TEXT NOT NULL,
        volunteer_name TEXT NOT NULL,
        recipient_id TEXT NOT NULL,
        recipient_name TEXT NOT NULL,
        status TEXT NOT NULL, -- assigned, picked_up, delivered
        assigned_at TEXT,
        picked_up_at TEXT,
        delivered_at TEXT,
        proof_notes TEXT
      );

      CREATE TABLE IF NOT EXISTS aid_requests (
        id TEXT PRIMARY KEY,
        recipient_id TEXT NOT NULL,
        recipient_name TEXT NOT NULL,
        servings_needed INTEGER NOT NULL,
        urgency TEXT NOT NULL, -- immediate, today, planned
        notes TEXT,
        status TEXT DEFAULT 'open',
        created_at TEXT
      );

      CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        urgency TEXT NOT NULL, -- emergency, high, medium, info
        donation_id TEXT,
        created_at TEXT
      );
    `);
  }

  // User queries
  getAllUsers() {
    return this.db.prepare(`SELECT * FROM users ORDER BY created_at DESC`).all();
  }

  getUserById(id) {
    return this.db.prepare(`SELECT * FROM users WHERE id = ?`).get(id);
  }

  getUsersByRole(role) {
    return this.db.prepare(`SELECT * FROM users WHERE role = ?`).all(role);
  }

  createUser(user) {
    const stmt = this.db.prepare(`
      INSERT INTO users (id, name, role, organization, phone, email, address, lat, lng, badge, rating, rescued_meals_count, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    stmt.run(
      user.id,
      user.name,
      user.role,
      user.organization || '',
      user.phone || '',
      user.email || '',
      user.address || '',
      user.lat || 0,
      user.lng || 0,
      user.badge || 'Community Contributor',
      user.rating || 5.0,
      user.rescued_meals_count || 0,
      user.created_at || new Date().toISOString()
    );
    return this.getUserById(user.id);
  }

  // Donation queries
  getAllDonations(filter = {}) {
    let sql = `SELECT * FROM donations WHERE 1=1`;
    const params = [];

    if (filter.status) {
      sql += ` AND status = ?`;
      params.push(filter.status);
    }
    if (filter.category) {
      sql += ` AND category = ?`;
      params.push(filter.category);
    }
    if (filter.food_type) {
      sql += ` AND food_type = ?`;
      params.push(filter.food_type);
    }
    if (filter.donor_id) {
      sql += ` AND donor_id = ?`;
      params.push(filter.donor_id);
    }
    if (filter.volunteer_id) {
      sql += ` AND volunteer_id = ?`;
      params.push(filter.volunteer_id);
    }
    if (filter.recipient_id) {
      sql += ` AND recipient_id = ?`;
      params.push(filter.recipient_id);
    }

    sql += ` ORDER BY 
      CASE status 
        WHEN 'available' THEN 1 
        WHEN 'claimed' THEN 2 
        WHEN 'in_transit' THEN 3 
        WHEN 'delivered' THEN 4 
        ELSE 5 
      END,
      expiry_time ASC`;

    return this.db.prepare(sql).all(...params);
  }

  getDonationById(id) {
    return this.db.prepare(`SELECT * FROM donations WHERE id = ?`).get(id);
  }

  createDonation(d) {
    const stmt = this.db.prepare(`
      INSERT INTO donations (
        id, donor_id, donor_name, title, description, category, food_type,
        servings, weight_kg, prepared_at, expiry_time, pickup_address,
        lat, lng, storage_instructions, packaging_type, allergens,
        status, recipient_id, recipient_name, volunteer_id, volunteer_name,
        claim_notes, verification_code, image_url, created_at
      ) VALUES (
        ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?,
        ?, ?, ?, ?
      )
    `);

    stmt.run(
      d.id,
      d.donor_id,
      d.donor_name,
      d.title,
      d.description || '',
      d.category,
      d.food_type,
      d.servings,
      d.weight_kg,
      d.prepared_at || new Date().toISOString(),
      d.expiry_time,
      d.pickup_address,
      d.lat,
      d.lng,
      d.storage_instructions || 'Keep in shaded, cool environment',
      d.packaging_type || 'Standard Food Safe Containers',
      d.allergens || 'None reported',
      d.status || 'available',
      d.recipient_id || null,
      d.recipient_name || null,
      d.volunteer_id || null,
      d.volunteer_name || null,
      d.claim_notes || null,
      d.verification_code || Math.floor(1000 + Math.random() * 9000).toString(),
      d.image_url || null,
      d.created_at || new Date().toISOString()
    );

    return this.getDonationById(d.id);
  }

  updateDonationStatus(id, status, extra = {}) {
    const donation = this.getDonationById(id);
    if (!donation) return null;

    let fields = [`status = ?`];
    let params = [status];

    if (extra.recipient_id !== undefined) {
      fields.push(`recipient_id = ?`);
      params.push(extra.recipient_id);
    }
    if (extra.recipient_name !== undefined) {
      fields.push(`recipient_name = ?`);
      params.push(extra.recipient_name);
    }
    if (extra.volunteer_id !== undefined) {
      fields.push(`volunteer_id = ?`);
      params.push(extra.volunteer_id);
    }
    if (extra.volunteer_name !== undefined) {
      fields.push(`volunteer_name = ?`);
      params.push(extra.volunteer_name);
    }
    if (extra.claim_notes !== undefined) {
      fields.push(`claim_notes = ?`);
      params.push(extra.claim_notes);
    }

    params.push(id);
    this.db.prepare(`UPDATE donations SET ${fields.join(', ')} WHERE id = ?`).run(...params);

    // If delivered, update donor and volunteer meal counts
    if (status === 'delivered') {
      const updated = this.getDonationById(id);
      if (updated.donor_id) {
        this.db.prepare(`UPDATE users SET rescued_meals_count = rescued_meals_count + ? WHERE id = ?`)
          .run(updated.servings, updated.donor_id);
      }
      if (updated.volunteer_id) {
        this.db.prepare(`UPDATE users SET rescued_meals_count = rescued_meals_count + ? WHERE id = ?`)
          .run(updated.servings, updated.volunteer_id);
      }
    }

    return this.getDonationById(id);
  }

  // Delivery tracking
  createDelivery(del) {
    const stmt = this.db.prepare(`
      INSERT INTO deliveries (id, donation_id, volunteer_id, volunteer_name, recipient_id, recipient_name, status, assigned_at, picked_up_at, delivered_at, proof_notes)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    stmt.run(
      del.id,
      del.donation_id,
      del.volunteer_id,
      del.volunteer_name,
      del.recipient_id,
      del.recipient_name,
      del.status || 'assigned',
      del.assigned_at || new Date().toISOString(),
      del.picked_up_at || null,
      del.delivered_at || null,
      del.proof_notes || null
    );
  }

  updateDeliveryStatus(donationId, status, proofNotes = '') {
    const now = new Date().toISOString();
    if (status === 'picked_up') {
      this.db.prepare(`UPDATE deliveries SET status = ?, picked_up_at = ? WHERE donation_id = ?`)
        .run(status, now, donationId);
    } else if (status === 'delivered') {
      this.db.prepare(`UPDATE deliveries SET status = ?, delivered_at = ?, proof_notes = ? WHERE donation_id = ?`)
        .run(status, now, proofNotes, donationId);
    }
  }

  getDeliveries(volunteerId = null) {
    if (volunteerId) {
      return this.db.prepare(`SELECT * FROM deliveries WHERE volunteer_id = ? ORDER BY assigned_at DESC`).all(volunteerId);
    }
    return this.db.prepare(`SELECT * FROM deliveries ORDER BY assigned_at DESC`).all();
  }

  // Aid Requests
  createAidRequest(req) {
    const stmt = this.db.prepare(`
      INSERT INTO aid_requests (id, recipient_id, recipient_name, servings_needed, urgency, notes, status, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);
    stmt.run(
      req.id,
      req.recipient_id,
      req.recipient_name,
      req.servings_needed,
      req.urgency || 'today',
      req.notes || '',
      req.status || 'open',
      req.created_at || new Date().toISOString()
    );
  }

  getAllAidRequests() {
    return this.db.prepare(`SELECT * FROM aid_requests ORDER BY created_at DESC`).all();
  }

  // Alerts
  createAlert(alert) {
    const stmt = this.db.prepare(`
      INSERT INTO alerts (id, title, message, urgency, donation_id, created_at)
      VALUES (?, ?, ?, ?, ?, ?)
    `);
    stmt.run(
      alert.id,
      alert.title,
      alert.message,
      alert.urgency || 'info',
      alert.donation_id || null,
      alert.created_at || new Date().toISOString()
    );
  }

  getRecentAlerts(limit = 10) {
    return this.db.prepare(`SELECT * FROM alerts ORDER BY created_at DESC LIMIT ?`).all(limit);
  }

  // Aggregate Impact & Analytics
  getImpactMetrics() {
    // Delivered donations count towards actual rescued impact
    const delivered = this.db.prepare(`
      SELECT 
        COALESCE(SUM(servings), 0) as total_meals,
        COALESCE(SUM(weight_kg), 0) as total_kg,
        COUNT(id) as total_deliveries
      FROM donations 
      WHERE status = 'delivered'
    `).get();

    // Active pipeline count
    const pipeline = this.db.prepare(`
      SELECT 
        COALESCE(SUM(servings), 0) as active_meals,
        COUNT(id) as active_listings
      FROM donations 
      WHERE status IN ('available', 'claimed', 'in_transit')
    `).get();

    // Environmental calculations standard in food waste metrics:
    // 1 kg food waste = ~2.5 kg CO2 equivalent greenhouse gases averted
    // 1 kg food waste = ~1,000 liters of freshwater conserved
    const totalKg = Number(delivered.total_kg || 0) + 1420; // baseline seeded impact
    const totalMeals = Number(delivered.total_meals || 0) + 3850;
    const co2AvoidedKg = Math.round(totalKg * 2.5);
    const waterSavedLiters = Math.round(totalKg * 1050);

    const categoryBreakdown = this.db.prepare(`
      SELECT category, COUNT(*) as count, SUM(servings) as total_servings
      FROM donations
      GROUP BY category
    `).all();

    return {
      total_meals: totalMeals,
      total_kg: Math.round(totalKg),
      co2_avoided_kg: co2AvoidedKg,
      water_saved_liters: waterSavedLiters,
      total_deliveries: Number(delivered.total_deliveries || 0) + 124,
      active_pipeline_meals: Number(pipeline.active_meals || 0),
      active_listings: Number(pipeline.active_listings || 0),
      categoryBreakdown
    };
  }

  getLeaderboard() {
    const topDonors = this.db.prepare(`
      SELECT id, name, organization, badge, rescued_meals_count, rating
      FROM users
      WHERE role = 'donor'
      ORDER BY rescued_meals_count DESC
      LIMIT 5
    `).all();

    const topVolunteers = this.db.prepare(`
      SELECT id, name, organization, badge, rescued_meals_count, rating
      FROM users
      WHERE role = 'volunteer'
      ORDER BY rescued_meals_count DESC
      LIMIT 5
    `).all();

    return { topDonors, topVolunteers };
  }
}

// Seed function to populate realistic live demo data
function seedDatabase(dbManager = new DatabaseManager()) {
  const now = Date.now();
  const hours = (h) => new Date(now + h * 3600 * 1000).toISOString();
  const pastHours = (h) => new Date(now - h * 3600 * 1000).toISOString();

  // Clean existing tables for fresh seed
  dbManager.db.exec(`
    DELETE FROM users;
    DELETE FROM donations;
    DELETE FROM deliveries;
    DELETE FROM aid_requests;
    DELETE FROM alerts;
  `);

  // Seed Users
  const users = [
    // Donors
    {
      id: 'usr-donor-1',
      name: 'Chef Rajesh Sharma',
      role: 'donor',
      organization: 'The Grand Heritage Banquet & Hotel',
      phone: '+91 98765 43210',
      email: 'banquets@grandheritage.com',
      address: 'Connaught Place, Central Avenue',
      lat: 28.6315,
      lng: 77.2167,
      badge: 'Zero-Waste Champion 🌟',
      rating: 4.9,
      rescued_meals_count: 1450
    },
    {
      id: 'usr-donor-2',
      name: 'Ananya Verma',
      role: 'donor',
      organization: 'Artisan Crust French Bakery & Cafe',
      phone: '+91 98111 22334',
      email: 'orders@artisancrust.org',
      address: 'Defence Colony Market, South Delhi',
      lat: 28.5729,
      lng: 77.2304,
      badge: 'Daily Fresh Donor 🥖',
      rating: 4.8,
      rescued_meals_count: 680
    },
    {
      id: 'usr-donor-3',
      name: 'Sunil Mehta',
      role: 'donor',
      organization: 'GreenMart Organic Supermarket & Hub',
      phone: '+91 99555 44112',
      email: 'surplus@greenmart.in',
      address: 'Indiranagar 100ft Road',
      lat: 28.5355,
      lng: 77.2625,
      badge: 'Fresh Produce Hero 🥦',
      rating: 4.9,
      rescued_meals_count: 920
    },
    {
      id: 'usr-donor-4',
      name: 'Pooja Iyer',
      role: 'donor',
      organization: 'CloudKitchen Express Co.',
      phone: '+91 97777 88990',
      email: 'sustainability@cloudkitchen.io',
      address: 'Cyber Hub Food District',
      lat: 28.4950,
      lng: 77.0895,
      badge: 'Tech Kitchen Savior 🍲',
      rating: 4.7,
      rescued_meals_count: 530
    },

    // Recipients / NGOs
    {
      id: 'usr-rec-1',
      name: 'Sister Mary Teresa',
      role: 'recipient',
      organization: 'Asha Child Hope Home & Orphanage',
      phone: '+91 98990 11223',
      email: 'care@ashachildcare.org',
      address: 'Lodhi Road Community Center',
      lat: 28.5916,
      lng: 77.2219,
      badge: 'Verified Shelter Partner 🛡️',
      rating: 5.0,
      rescued_meals_count: 2100
    },
    {
      id: 'usr-rec-2',
      name: 'Harpreet Singh',
      role: 'recipient',
      organization: 'Langar Seva Community Food Bank',
      phone: '+91 98100 99887',
      email: 'langar@sevabank.org',
      address: 'Karol Bagh Gurudwara Relief Center',
      lat: 28.6514,
      lng: 77.1907,
      badge: 'High-Capacity Kitchen 🍲',
      rating: 4.9,
      rescued_meals_count: 3200
    },
    {
      id: 'usr-rec-3',
      name: 'Dr. Fatima Khan',
      role: 'recipient',
      organization: 'Prerna Slum Relief & Evening School',
      phone: '+91 97112 33445',
      email: 'relief@prernango.in',
      address: 'Okhla Phase 1 Outreach Point',
      lat: 28.5284,
      lng: 77.2793,
      badge: 'Direct Relief Responder 🤝',
      rating: 4.8,
      rescued_meals_count: 1450
    },

    // Volunteers
    {
      id: 'usr-vol-1',
      name: 'Kabir Das',
      role: 'volunteer',
      organization: 'Food Runners Youth Chapter',
      phone: '+91 99101 20202',
      email: 'kabir.runner@rescue.org',
      address: 'Lajpat Nagar Ring Road',
      lat: 28.5678,
      lng: 77.2433,
      badge: 'Rapid Rescue Hero ⚡',
      rating: 5.0,
      rescued_meals_count: 420
    },
    {
      id: 'usr-vol-2',
      name: 'Simran Kaur',
      role: 'volunteer',
      organization: 'CleanPlate Biker Squad',
      phone: '+91 98222 34567',
      email: 'simran.biker@rescue.org',
      address: 'Hauz Khas Enclave',
      lat: 28.5494,
      lng: 77.2001,
      badge: 'Night Patrol Knight 🌙',
      rating: 4.9,
      rescued_meals_count: 310
    },

    // Admin
    {
      id: 'usr-admin-1',
      name: 'Antigravity Rescue Coordinator',
      role: 'admin',
      organization: 'Food Rescue Revolution HQ',
      phone: '+91 11 2345 6789',
      email: 'hq@foodrescuerevolution.org',
      address: 'National Sustainability Center, New Delhi',
      lat: 28.6139,
      lng: 77.2090,
      badge: 'Central Dispatch Admin 🌐',
      rating: 5.0,
      rescued_meals_count: 9500
    }
  ];

  for (const u of users) {
    dbManager.createUser(u);
  }

  // Seed Realistic Active & Recent Donations
  const donations = [
    {
      id: 'don-101',
      donor_id: 'usr-donor-1',
      donor_name: 'The Grand Heritage Banquet & Hotel',
      title: 'Royal Shahi Paneer, Dal Makhani & Jeera Rice Buffet Surplus',
      description: 'Catered corporate dinner concluded 1 hour ago. Pristine condition, preserved in temperature-regulated insulated food warmers. Cooked with high hygiene standards.',
      category: 'cooked_meals',
      food_type: 'veg',
      servings: 85,
      weight_kg: 34.0,
      prepared_at: pastHours(2),
      expiry_time: hours(2.5), // Urgent! 2.5 hours remaining
      pickup_address: 'Banquet Hall 3, Grand Heritage Hotel, Connaught Place',
      lat: 28.6315,
      lng: 77.2167,
      storage_instructions: 'Keep warm (>65°C) or chill immediately below 4°C upon delivery',
      packaging_type: 'Commercial Stainless Steel insulated urns + bio food boxes',
      allergens: 'Contains Dairy (Paneer, Cream). Gluten-free rice.',
      status: 'available',
      verification_code: '4821',
      image_url: 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'don-102',
      donor_id: 'usr-donor-2',
      donor_name: 'Artisan Crust French Bakery & Cafe',
      title: 'Artisanal Sourdough Loaves, Croissants & Brioche Buns',
      description: 'Fresh evening bakery surplus. Baked this morning at 6 AM. Ideal for evening shelter snacks or breakfast for kids.',
      category: 'bakery',
      food_type: 'veg',
      servings: 50,
      weight_kg: 18.5,
      prepared_at: pastHours(10),
      expiry_time: hours(14), // Plenty of time
      pickup_address: 'Shop 14, Defence Colony Main Market, New Delhi',
      lat: 28.5729,
      lng: 77.2304,
      storage_instructions: 'Keep dry at room temperature in food-grade kraft bags',
      packaging_type: 'Sealed individual craft bakery bags',
      allergens: 'Contains Wheat/Gluten. Croissants contain butter.',
      status: 'available',
      verification_code: '7193',
      image_url: 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'don-103',
      donor_id: 'usr-donor-3',
      donor_name: 'GreenMart Organic Supermarket & Hub',
      title: 'Crate of Ripe Organic Apples, Bananas & Spinach Bunches',
      description: 'Slightly surface-blemished but 100% wholesome ripe fruits and leafy greens diverted from retail shelves. Perfect for juicing or nutritional salads.',
      category: 'fresh_produce',
      food_type: 'vegan',
      servings: 120,
      weight_kg: 55.0,
      prepared_at: pastHours(6),
      expiry_time: hours(28),
      pickup_address: 'Loading Bay #2, GreenMart Hub, Indiranagar',
      lat: 28.5355,
      lng: 77.2625,
      storage_instructions: 'Keep in ventilated cool crates',
      packaging_type: 'Eco-friendly wooden & stackable plastic crates',
      allergens: 'None (Pure vegan organic produce)',
      status: 'claimed',
      recipient_id: 'usr-rec-1',
      recipient_name: 'Asha Child Hope Home & Orphanage',
      claim_notes: 'Urgent nutritional need for 80 children at shelter.',
      verification_code: '3318',
      image_url: 'https://images.unsplash.com/photo-1610832958506-aa56368176cf?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'don-104',
      donor_id: 'usr-donor-4',
      donor_name: 'CloudKitchen Express Co.',
      title: 'Nutritious Veggie Pulao & Spiced Lentil Curry Bento Boxes',
      description: 'Surplus individual portion bento meals prepared for canceled corporate lunch order. Individually heat-sealed with tamper-evident tape.',
      category: 'cooked_meals',
      food_type: 'veg',
      servings: 40,
      weight_kg: 16.0,
      prepared_at: pastHours(3),
      expiry_time: hours(3.5),
      pickup_address: 'Hub 4, Cyber City Gate 2, DLF Phase 2',
      lat: 28.4950,
      lng: 77.0895,
      storage_instructions: 'Keep sealed; warm up before consumption',
      packaging_type: 'BPA-free compostable meal trays with seal',
      allergens: 'Contains Mustard, cumin, mild spices',
      status: 'in_transit',
      recipient_id: 'usr-rec-2',
      recipient_name: 'Langar Seva Community Food Bank',
      volunteer_id: 'usr-vol-1',
      volunteer_name: 'Kabir Das',
      claim_notes: 'Heading towards Karol Bagh hub in cargo scooter.',
      verification_code: '9045',
      image_url: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80'
    },
    {
      id: 'don-105',
      donor_id: 'usr-donor-1',
      donor_name: 'The Grand Heritage Banquet & Hotel',
      title: 'Tandoori Chicken & Mutton Seekh Kebabs (Delivered Yesterday)',
      description: 'Delivered successfully to Prerna Relief center yesterday evening.',
      category: 'cooked_meals',
      food_type: 'non_veg',
      servings: 90,
      weight_kg: 38.0,
      prepared_at: pastHours(26),
      expiry_time: pastHours(18),
      pickup_address: 'Connaught Place Main Kitchen',
      lat: 28.6315,
      lng: 77.2167,
      storage_instructions: 'Insulated hot carriers',
      packaging_type: 'Aluminum foil trays',
      allergens: 'Poultry, mutton, dairy marinade',
      status: 'delivered',
      recipient_id: 'usr-rec-3',
      recipient_name: 'Prerna Slum Relief & Evening School',
      volunteer_id: 'usr-vol-2',
      volunteer_name: 'Simran Kaur',
      claim_notes: 'Fed 90 families in evening distribution drive.',
      verification_code: '1234',
      image_url: 'https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?auto=format&fit=crop&w=600&q=80'
    }
  ];

  for (const d of donations) {
    dbManager.createDonation(d);
  }

  // Seed Deliveries
  dbManager.createDelivery({
    id: 'del-01',
    donation_id: 'don-104',
    volunteer_id: 'usr-vol-1',
    volunteer_name: 'Kabir Das',
    recipient_id: 'usr-rec-2',
    recipient_name: 'Langar Seva Community Food Bank',
    status: 'picked_up',
    assigned_at: pastHours(1),
    picked_up_at: pastHours(0.3),
    proof_notes: 'Picked up 40 sealed bento boxes. Hot and fresh. En route.'
  });

  dbManager.createDelivery({
    id: 'del-02',
    donation_id: 'don-105',
    volunteer_id: 'usr-vol-2',
    volunteer_name: 'Simran Kaur',
    recipient_id: 'usr-rec-3',
    recipient_name: 'Prerna Slum Relief & Evening School',
    status: 'delivered',
    assigned_at: pastHours(24),
    picked_up_at: pastHours(23),
    delivered_at: pastHours(22),
    proof_notes: 'Delivered directly to Community Kitchen Head. Verified with OTP 1234.'
  });

  // Seed Aid Requests from Shelters
  dbManager.createAidRequest({
    id: 'req-01',
    recipient_id: 'usr-rec-1',
    recipient_name: 'Asha Child Hope Home & Orphanage',
    servings_needed: 65,
    urgency: 'immediate',
    notes: 'Urgent dinner requirement for 65 children aged 5-16. Rice, lentils or bread rolls preferred.',
    status: 'open'
  });

  dbManager.createAidRequest({
    id: 'req-02',
    recipient_id: 'usr-rec-3',
    recipient_name: 'Prerna Slum Relief & Evening School',
    servings_needed: 100,
    urgency: 'today',
    notes: 'Evening school meal distribution for undernourished children and mothers in Okhla.',
    status: 'open'
  });

  // Seed Alerts
  dbManager.createAlert({
    id: 'alt-01',
    title: '🚨 Urgent Rescue Required: 85 Servings in Connaught Place',
    message: 'The Grand Heritage Banquet has 85 hot meals expiring within 2.5 hours! Looking for nearest NGO or volunteer runner.',
    urgency: 'emergency',
    donation_id: 'don-101'
  });

  dbManager.createAlert({
    id: 'alt-02',
    title: '🚚 Volunteer Dispatched for CloudKitchen Surplus',
    message: 'Volunteer Kabir Das has picked up 40 bento boxes and is heading to Langar Seva Food Bank.',
    urgency: 'info',
    donation_id: 'don-104'
  });

  console.log('✅ Food Rescue Revolution database initialized & seeded successfully.');
}

module.exports = {
  DatabaseManager,
  seedDatabase,
  DB_PATH
};

// Auto seed if executed directly
if (require.main === module) {
  seedDatabase();
}
