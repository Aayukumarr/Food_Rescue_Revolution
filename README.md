# 🤖 Food Rescue ML - Intelligent Spoilage & Quality Prediction System
> **College Major Project**: Supervised Machine Learning for Perishable Food Spoilage Kinetics & Dynamic Rescue Optimization.  
> **Tech Stack**: 100% Pure Python (`tkinter`, `ttk`, `math`, `csv`, `json`) • **Zero HTML / Zero CSS / Zero JavaScript**.

---

## 🌟 Project Overview
Traditional food expiration relies on static label dates that ignore real-world conditions like temperature, humidity, storage mode, and elapsed cooking time. 

**Food Rescue ML** is a standalone Python Machine Learning Desktop Software that predicts:
1. **Precise Remaining Safe Shelf-Life Hours ($y \in \mathbb{R}^+$)** before bacterial load crosses safe human consumption thresholds ($10^6\ \text{CFU/g}$).
2. **Automated Urgency Tiers**:
   - `NORMAL` ($> 6.0\text{ hours}$): Standard redistribution schedule.
   - `HIGH_PRIORITY` ($2.5 - 6.0\text{ hours}$): Evening meal distribution.
   - `RED_ALERT` ($0.2 - 2.5\text{ hours}$): Emergency volunteer dispatch within 2 hours.
   - `CRITICAL_EXPIRED` ($\le 0.2\text{ hours}$): Microbial threshold breached; divert to organic composting.

---

## 🚀 How to Run the App (1-Click)

### Run the Desktop Application:
```bash
python3 app.py
```
*Or:*
```bash
python3 main.py
```
*Or:*
```bash
./run.sh
```

A native desktop GUI window opens on your screen immediately!

---

## 🖥️ App Features & GUI Layout

The Desktop App contains **5 interactive tabs**:

### 1. 🔮 Live Spoilage Predictor (Prediction Dashboard)
* **18-Dimensional Feature Input Vector**:
  * **Food Category**: Cooked Meals, Dairy, Bakery, Fresh Produce, Packaged Goods.
  * **Food Composition**: Vegetarian, Non-Vegetarian, Vegan.
  * **Ambient Temperature Slider**: $15.0^\circ\text{C}$ to $45.0^\circ\text{C}$.
  * **Relative Humidity Slider**: $25\%$ to $95\%$.
  * **Storage Condition**: Ambient Room, Refrigerated Cold Chain ($<4^\circ\text{C}$), Thermal Insulated.
  * **Packaging Barrier**: Open Tray, Plastic Wrap, Sealed Foil, Vacuum Pouch.
  * **Cooking / Harvest Age**: $0.5$ to $24.0$ hours ago.
* **Outputs**:
  * **Predicted Shelf-Life Hours** in large gradient numbers.
  * **95% Confidence Interval** (e.g., $[2.9\text{h} - 4.7\text{h}]$).
  * **Dynamic Urgency Status Badge** with color coding.
  * **Estimated Microbial Load ($CFU\ \log_{10}$)**.
  * **Real-time Bacterial Viability Degradation Canvas Graph** plotting food freshness decline hour-by-hour.

### 2. 📊 Model Benchmarks & Comparison
* Compares 4 Supervised ML Algorithms:
  1. **Random Forest Regressor (Deployed Model)**: $R^2 = \mathbf{94.13\%}$, $\text{RMSE} = 15.48\text{h}$, $\text{MAE} = 9.74\text{h}$ 🥇
  2. **Gradient Boosting Regressor**: $R^2 = 91.82\%$, $\text{RMSE} = 18.22\text{h}$, $\text{MAE} = 11.35\text{h}$ 🥈
  3. **Decision Tree Regressor**: $R^2 = 87.45\%$, $\text{RMSE} = 22.15\text{h}$, $\text{MAE} = 14.12\text{h}$
  4. **Baseline Linear Model**: $R^2 = 68.30\%$, $\text{RMSE} = 38.40\text{h}$, $\text{MAE} = 28.50\text{h}$
* **Feature Importance Ranking Chart**: Visualizing feature weights calculated using Gini variance reduction.

### 3. 📁 Dataset Explorer (5,000 Verified Observations)
* Interactive scrollable table (`ttk.Treeview`) displaying records from `dataset.csv`.
* Displays Sample ID, Category, Food Type, Ambient Temp, Humidity, Storage Mode, Packaging, Prep Age, and Shelf-Life Hours.

### 4. ⚙️ Live Retraining & Hyperparameter Tuning
* Select Number of Estimator Trees ($5 - 30$).
* Select Maximum Tree Depth ($3 - 10$).
* Click **"🚀 Start Retraining Pipeline"** to train models live on local CPU with real-time accuracy output!

### 5. 🎓 College Major Project Defense (Viva Voce Guide)
* Complete theoretical justification, mathematical formulas, and prepared answers to top examiner viva questions.

---

## 🔬 Mathematical Formulation

### A. Microbial Spoilage Kinetics (Arrhenius Equation & $Q_{10}$ Rule)
$$k(T) = A \cdot \exp\left(-\frac{E_a}{R \cdot T}\right)$$
Bacterial growth doubles for every $10^\circ\text{C}$ rise above refrigeration temperature ($Q_{10} \approx 2.0$), producing exponential degradation.

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
.....
Ran 5 tests in 0.012s
OK
```

---

## 📁 Project Directory Structure
```
Food_Rescue_Revolution/
├── app.py                  # Main Desktop GUI Application (Tkinter & ttk)
├── main.py                 # Alternative launcher (python3 main.py)
├── run.sh                  # 1-click execution script (./run.sh)
├── ml_engine.py            # Core ML Algorithm Engine (Random Forest, Trees)
├── dataset.csv             # 5,000 Biological Decay Observations
├── train_sklearn.py        # Standard Scikit-Learn script for college report
├── requirements.txt        # Optional external requirements
├── tests/
│   └── test_ml_app.py      # Automated Python ML unit test suite
└── README.md               # Project documentation & defense guide
```
