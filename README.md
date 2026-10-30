# 🌱 Food Rescue Revolution

> **Zero Hunger. Zero Food Waste. Real-Time Climate Impact.**  
> A full-stack web platform connecting surplus food donors (banquets, restaurants, bakeries, supermarkets) with NGOs, shelters, and volunteer runners to rescue edible food before it reaches landfills.

---

## 🌟 Overview

Globally, over **1/3rd of all food produced is wasted**, while hundreds of millions face hunger. Food decomposing in landfills generates methane—a greenhouse gas 25x more potent than carbon dioxide.

**Food Rescue Revolution** solves this mismatch with a real-time, proximity-aware redistribution ecosystem:
- 👨‍🍳 **Donors** list surplus food in 30 seconds with safe consumption windows and dietary tags.
- 🏛️ **Shelters & NGOs** claim needed portions based on hunger relief demand.
- 🛵 **Volunteer Runners** accept delivery tasks and verify deliveries using digital OTP security.
- 📊 **Carbon Tracker** quantifies meals saved, landfill waste averted, and CO2 emissions avoided.
- 🤖 **Smart Food Safety Advisor** calculates shelf life using HACCP temperature guidelines.

---

## 🚀 Key Features

| Feature | Description |
| :--- | :--- |
| **🍲 Surplus Marketplace** | Live cards with **second-by-second countdown timers** (`02h 45m left`), dietary badges (100% Veg, Vegan, Non-Veg), category filters, and direct claim buttons. |
| **🗺️ Interactive Rescue Map** | Real-time OpenStreetMap (Leaflet) pins tracking available surplus (green), claimed batches (yellow), volunteer runs (purple), and registered shelters (blue). |
| **⚡ Real-Time Live Sync (SSE)** | Built-in Server-Sent Events stream: New listings, claims, and deliveries update automatically across all screens without reloading. |
| **🛵 Volunteer Mission Dispatch** | Route assignment and secure **4-digit OTP handover verification** to guarantee safe food arrival. |
| **🏛️ Shelter Emergency SOS** | NGOs can broadcast urgent meal aid requests during shortages or crisis relief. |
| **📊 Environmental Impact Engine** | Interactive Chart.js graphs tracking monthly rescue trends, category distribution, CO2e offsets (1 kg food ≈ 2.5 kg CO2e), and donor leaderboards. |
| **🤖 AI Food Safety Advisor** | Analyzes ambient temperature, hours since cooking, and food type to assess safe distribution viability and safety index. |
| **🔄 Instant Role Switcher** | Switch between Donor, NGO, Volunteer, and Admin modes with 1 click to test every perspective effortlessly. |

---

## 🏗️ Architecture & Tech Stack

- **Backend**: Node.js (Built-in HTTP server, SSE engine, REST API)
- **Database**: SQLite (Node.js built-in `node:sqlite` — **Zero external binary dependencies required!**)
- **Frontend**: Single-Page Application (HTML5, Tailwind CSS, Modern Glassmorphism CSS, Vanilla ES6 Modules)
- **Maps**: Leaflet.js with OpenStreetMap (Tile caching & custom animated pins)
- **Visualizations**: Chart.js (Carbon avoidance trends & food category distribution)
- **Test Framework**: Node.js built-in `node:test` and `node:assert` (10/10 automated tests passing)

---

## 🖥️ 3 Dedicated Portals & Dashboards

The application is structured into **3 specialized, fully functional dashboards**:

```
                                ┌────────────────────────────────────────┐
                                │      Food Rescue Revolution System     │
                                └────────────────────────────────────────┘
                                     │               │              │
                   ┌─────────────────┴─┐      ┌──────┴─────┐  ┌─────┴────────────────┐
                   ▼                   ▼      ▼            ▼  ▼                      ▼
        👨‍🍳 1. Donor Dashboard        🏛️ 2. NGO Dashboard    🛡️ 3. Admin Command Center
        (Jo Food Donate Karega)       (Enjio / Shelter Hub)   (Central Operations & HQ)
        • Post Surplus in 30s         • Real-time Claiming    • Full Metro Ops Map
        • Live Expiry Countdown       • Gate Handover OTPs    • Master Donations Table
        • Shelter Needs Radar         • Inbound Pipeline      • Partner Verification
        • Carbon Offset Stats         • Emergency Meal SOS    • System-Wide Red Alerts
```

### 1. 👨‍🍳 Donor Dashboard ("Jo Donate Karega")
* **Purpose**: For Restaurants, Hotels, Banquets, Bakeries, Supermarkets, and Caterers.
* **Security & Authentication**:
  * **Password Protected Gatekeeper**: Requires Donor Password (`donor123`) before accessing the portal.
  * **Session Controls**: Instant "🔒 Logout" button and "🔑 Password" change tool in banner.
* **Key Features**:
  * **Surplus Food Listing Form**: Post dishes with portion count, weight, dietary flags (Veg/Vegan/Non-Veg), and safe consumption window.
  * **AI Shelf-Life Calculator**: Pre-screen safety before posting.
  * **My Active Listings**: Live second-by-second countdown timer on all food items.
  * **Shelter Relief Radar**: Nearby shelters in urgent need of dinner tonight with 1-click "Donate to this Shelter" fulfillment.
  * **Impact Metrics**: Total Meals Rescued, Total kg diverted, CO2e averted.

### 2. 🏛️ NGO / Shelter Dashboard ("Enjio Ka Portal")
* **Purpose**: For Orphanages, Community Kitchens, Shelters, and Food Banks.
* **Security & Authentication**:
  * **Password Protected Gatekeeper**: Requires NGO Password (`ngo123`) before accessing relief controls.
  * **Session Controls**: Instant "🔒 Logout" button and "🔑 Password" change tool in banner.
* **Key Features**:
  * **Surplus Food Claiming**: Browse available surplus food batches within city radius and claim with 1-click.
  * **Gate Handover OTP Display**: Displays the **4-digit Security OTP (e.g., `4821`)** prominently so the shelter manager can provide it to the volunteer upon food arrival.
  * **Inbound Delivery Tracker**: Live status of volunteer riders en route (`🛵 In Transit`).
  * **Broadcast Urgent Meal Need (SOS)**: Alert nearby restaurants when the shelter kitchen runs short of meals for tonight.

### 3. 🛡️ Admin Dashboard ("Admin Ka Command Center")
* **Purpose**: For Central Platform Operations and City Dispatch Coordinators.
* **Security & Authentication**:
  * **Password Protected Gatekeeper**: Requires Admin Password (`admin123`) before granting access to central controls.
  * **Session Management**: Session lock and instant Logout button.
  * **Change Password**: In-dashboard security tool to update the Admin password anytime.
* **Key Features**:
  * **Network-Wide KPIs**: Total meals rescued, kg food diverted, carbon offset, active rescue runs in-flight.
  * **Interactive Operations Map**: Real-time Leaflet map showing all live donations (green), claimed batches (orange), and registered shelters (blue).
  * **Master Donations Registry Table**: Full control over all city listings with "Mark Delivered" and "Delete/Cancel" powers.
  * **Partner Verification Directory**: Verify NGOs and Donors with "Verified Partner 🌟" badges.
  * **Network Red Alert Broadcaster**: Push emergency alerts to all screens simultaneously.

---

## ⚡ Quick Start Guide

### 1. Requirements
- Node.js **v18+** (Node v22 installed on this machine).
- **No `npm install` required!** The application is zero-dependency and runs straight out of the box.

### 2. Start the Application
```bash
npm start
```
*Or:*
```bash
node server.js
```

Then open your browser at:
👉 **[http://localhost:3000](http://localhost:3000)**

---

## 🧪 Running Automated Tests

Run the comprehensive test suite (testing all endpoints, static file serving, and the complete rescue lifecycle):
```bash
npm test
```

Expected output:
```text
✔ GET / should serve index.html with 200 OK
✔ GET /styles.css should serve CSS file
✔ GET /app.js should serve client JavaScript
✔ GET /api/health should return online status
✔ GET /api/donations should return list of seeded donations
✔ GET /api/impact should return carbon and meal statistics
✔ GET /api/leaderboard should return top donors and volunteers
✔ Complete Rescue Lifecycle: Create -> Claim -> Assign Volunteer -> Verify Delivery
✔ POST /api/ai-advisor/analyze calculates shelf life and urgency
✔ POST & GET /api/aid-requests handles shelter requests
ℹ tests 10
ℹ pass 10
```

---

## 📡 REST API Reference

### Food Donations
- `GET /api/donations` — List all surplus listings (supports `?status=`, `?category=`, `?food_type=`).
- `POST /api/donations` — Create a new surplus listing (broadcasts live alert via SSE).
- `GET /api/donations/:id` — Get single donation details.
- `POST /api/donations/:id/claim` — NGO claims surplus food.
- `POST /api/donations/:id/assign-volunteer` — Volunteer accepts pickup and delivery mission.
- `POST /api/donations/:id/verify-delivery` — Recipient confirms handover using 4-digit OTP.

### Impact & Leaderboards
- `GET /api/impact` — Aggregate metrics: Total meals, Landfill kg, CO2e prevented, Water conserved.
- `GET /api/leaderboard` — Top donors and volunteer rankings.

### Emergency Aid & Alerts
- `GET /api/alerts` — Recent urgent surplus notifications.
- `POST /api/alerts` — Broadcast emergency alert.
- `GET /api/aid-requests` — Community shelter meal requests.
- `POST /api/aid-requests` — Submit new urgent shelter request.

### AI Safety Advisor
- `POST /api/ai-advisor/analyze` — Evaluates food category, temperature, and preparation time to return safety score, remaining safe window, and HACCP guidelines.

### Real-Time Live Feed
- `GET /api/events` — Server-Sent Events (SSE) stream for real-time notification pushes.

### Database Controls
- `POST /api/seed` — Resets and seeds the SQLite database with realistic metro sample data.

---

## 📂 Project Directory Structure

```
Food_Rescue_Revolution/
├── server.js            # Core HTTP server, REST API, SSE broadcaster, and static file server
├── db.js                # SQLite Database schema, queries, and realistic metro seed data
├── package.json         # Project metadata and test/run scripts
├── .gitignore           # Ignored files (node_modules, logs)
├── README.md            # Complete project documentation
├── tests/
│   └── api.test.js      # 10 automated test cases for all endpoints and workflows
└── public/
    ├── index.html       # Full SPA UI: Navbar, Hero, Marketplace, Map, Modals, Forms
    ├── styles.css       # Custom glassmorphic styling, pulse animations, cards, badges
    └── app.js           # Client state, Leaflet map, Chart.js, SSE listener, filters
```

---

## 💡 Role-Based User Scenarios (For Live Demo)

Use the **Active Role** dropdown in the top navigation bar to test all user personas:
1. **Donor Mode (Chef Rajesh Sharma)**: Click `+ Donate Food` to list wedding or banquet surplus. Watch it instantly appear on the live map and marketplace with a countdown badge!
2. **NGO / Shelter Mode (Sister Mary Teresa)**: Click `Claim Food 🤝` on any available listing. The status updates across all connected browsers in real-time.
3. **Volunteer Runner Mode (Kabir Das)**: Visit the **Volunteer Missions** tab to accept claimed runs (`🛵 Accept Pickup Run`), then complete handover by entering the 4-digit OTP.
4. **Impact & Admin Mode**: Watch the live counters for **Meals Rescued** and **CO2e Prevented** increase automatically when food is delivered!

---

## 🌍 Environmental Impact Metrics

- **1 kg Food Waste Rescued** = **~2.5 kg CO2e greenhouse gas avoided** from landfill decomposition.
- **1 kg Food Waste Rescued** = **~1,050 liters of agricultural freshwater conserved**.
- **1 Meal Saved** = **~0.4 kg of nutritious food**.

---

## 📜 License
MIT License. Built for social good and sustainability.

