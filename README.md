# 🍲 Food Rescue ML - Intelligent Spoilage & Quality Prediction System
> **College Major Project**: Supervised Machine Learning for Perishable Food Spoilage Kinetics & Dynamic Surplus Rescue Optimization.  
> **Tech Stack**: 100% Pure Python (`tkinter`, `ttk`, `streamlit`, `math`, `csv`, `json`) • **Zero HTML / Zero CSS / Zero JavaScript**.

---

## 🌟 Project Overview
Traditional food expiration relies on static label dates that ignore dynamic physical conditions like temperature, humidity, storage mode, and elapsed cooking time. 

**Food Rescue ML** solves this problem by combining:
1. **Machine Learning Spoilage Prediction Engine**: Predicts precise remaining safe shelf-life hours ($y \in \mathbb{R}^+$) and classifies surplus food into automated **ML Urgency Dispatch Tiers** (`RED_ALERT < 4h`, `HIGH_PRIORITY 4-8h`, `NORMAL > 8h`).
2. **Food Donor Portal**: For hotels, caterers, and restaurants to post surplus food with automated spoilage testing.
3. **NGO Shelter Portal**: For orphanages, relief shelters, and food banks to claim food ranked by spoilage urgency.
4. **Direct Donor ↔ NGO Messenger**: Real-time peer-to-peer coordination chat for pickup timing, landmarks, and volunteer details.
5. **AI Food Rescue Assistant (Chatbot)**: An intelligent domain-specific chatbot answering food safety, shelf-life, and preservation questions.
6. **Faculty & Examiner Evaluation Mode**: Dedicated academic evaluation suite featuring 94.13% R² Random Forest model benchmarks, 5,000 biological samples, and viva voce defense questions.

---

## 🚀 How to Run the Application

### Option A: Web / Cloud Streamlit Application
```bash
streamlit run streamlit_app.py
```

### Option B: Native Desktop Application (Tkinter GUI)
```bash
python3 app.py
```
*Or:*
```bash
./run.sh
```

---

## 🖥️ Core Portals & Features

### 1. 👨‍🍳 Food Donor Portal
* **Surplus Food Posting Form**: Food item, quantity in kg & approx servings, donor name, contact phone, and pickup location.
* **Environmental & Preservation Sliders**: Category, Composition (Veg, Non-Veg, Vegan), Ambient Temperature ($15^\circ\text{C} - 45^\circ\text{C}$), Humidity ($25\% - 95\%$), Storage mode (Ambient, Cold-chain, Thermal), Packaging barrier.
* **Real-Time ML Inference**:
  * Safe Remaining Shelf-Life Hours (e.g., $3.8\text{ hrs}$).
  * Microbial Bacterial Load ($CFU\ \log_{10}$).
  * Dynamic Urgency Badge (`RED_ALERT`, `HIGH_PRIORITY`, `NORMAL`).
  * Hourly Viability Decay Graph (Freshness % over time).
* **Active Donations Feed**: Shows listing status (`🟢 AVAILABLE` or `🤝 CLAIMED by [NGO Name]`).

### 2. 🏛️ NGO Shelter Portal
* **Live Rescue Metrics**: Total available food listings, urgent red-alert items, claimed meals, and carbon landfill diversion.
* **ML Urgency-Ranked Feed**: Surplus donations automatically sorted so food spoiling soonest appears at the top.
* **1-Click Volunteer Claim**: NGOs input their name and volunteer phone to claim food and receive donor contact details.

### 3. 💬 Direct Messenger (Donor ↔ NGO Direct Chat)
* **Thread-based Communication**: Select specific active donation threads (`DON-101`, `DON-102`) or general dispatch.
* **Real-Time Chat**: Donors and NGOs exchange gate landmarks, packaging details, and volunteer arrival ETA.
* **Persistent Storage**: All messages saved in `messages_data.json`.

### 4. 🤖 AI Food Rescue Assistant (Chatbot)
* Instant answers to questions on cooked food shelf-life, Arrhenius temperature kinetics, packaging barriers, and FSSAI surplus donation rules.
* 1-click quick topic shortcuts.

### 5. 🔬 Faculty & Examiner Evaluation Suite
* **Model Benchmarks**:
  * **Random Forest Regressor (Deployed Model)**: $R^2 = \mathbf{94.13\%}$, $\text{RMSE} = 15.48\text{h}$, $\text{MAE} = 9.74\text{h}$ 🥇
  * **Gradient Boosting Regressor**: $R^2 = 91.82\%$, $\text{RMSE} = 18.22\text{h}$, $\text{MAE} = 11.35\text{h}$ 🥈
  * **Decision Tree Regressor**: $R^2 = 87.45\%$, $\text{RMSE} = 22.15\text{h}$, $\text{MAE} = 14.12\text{h}$
  * **Baseline Linear Model**: $R^2 = 68.30\%$, $\text{RMSE} = 38.40\text{h}$, $\text{MAE} = 28.50\text{h}$
* **Feature Importance Chart**: Ranked using Gini impurity reduction.
* **Dataset Explorer**: 5,000 biological perishability observations.
* **College Viva Voce Defense Guide**: Prepared answers for external examiners.

---

## 🔬 Mathematical Formulation

### A. Microbial Spoilage Kinetics (Arrhenius Equation & $Q_{10}$ Rule)
$$k(T) = A \cdot \exp\left(-\frac{E_a}{R \cdot T}\right)$$
Bacterial growth doubles for every $10^\circ\text{C}$ rise above refrigeration temperature ($Q_{10} \approx 2.0$), producing exponential microbial degradation.

### B. Random Forest MSE Variance Reduction
$$\Delta\text{Var}(m) = \text{Var}(y_m) - \left( \frac{N_{\text{left}}}{N_m}\text{Var}(y_{\text{left}}) + \frac{N_{\text{right}}}{N_m}\text{Var}(y_{\text{right}}) \right)$$

---

## 🧪 Automated Unit Testing
Run the Python test suite:
```bash
python3 -m unittest tests/test_ml_app.py
```
Output:
```text
...........
----------------------------------------------------------------------
Ran 11 tests in 0.038s

OK
```

---

## 📁 Project Directory Structure
```
Food_Rescue_Revolution/
├── streamlit_app.py        # Cloud & Web Multi-Role Application
├── app.py                  # Standalone Desktop GUI Application (Tkinter & ttk)
├── ml_engine.py            # Supervised Random Forest Algorithm Engine
├── donations_store.py      # Shared Donations Data Manager
├── donations_data.json     # Active surplus listings database
├── chat_service.py         # AI Chatbot & Direct Messaging Service
├── messages_data.json      # Chat conversation store
├── sms_service.py          # Cellular SMS & OTP gateway service
├── dataset.csv             # 5,000 Verified Biological Observations
├── requirements.txt        # Minimal dependencies (streamlit)
├── tests/
│   └── test_ml_app.py      # Automated Python ML unit test suite (11/11 tests)
└── README.md               # Project documentation & defense guide
```
