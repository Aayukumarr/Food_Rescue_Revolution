# 🤖 Machine Learning Intelligence Subsystem
## Food Rescue Revolution: Spoilage Kinetics & Dynamic Surplus Redistribution

> **Major Project Component**: Supervised Machine Learning for Food Perishability, Microbial Growth Estimation, and Urgency-Tier Classification.

---

### 1. Project Motivation & ML Problem Statement
In traditional food rescue, static expiry dates fail because food degradation is non-linear and heavily influenced by **ambient temperature, relative humidity, food composition (water activity $a_w$), storage conditions, and packaging integrity**. 

* **Objective 1 (Regression Task)**: Predict precise **remaining safe shelf-life hours ($y \in \mathbb{R}^+$)** before bacterial colony count exceeds the safe microbial threshold ($10^6\ \text{CFU/g}$).
* **Objective 2 (Classification Task)**: Classify the shipment into 4 real-time dispatch urgency tiers:
  1. `NORMAL` ($> 6.0\text{ hours}$): Standard local shelter delivery.
  2. `HIGH_PRIORITY` ($2.5 - 6.0\text{ hours}$): Fast-track evening distribution.
  3. `RED_ALERT` ($0.2 - 2.5\text{ hours}$): Immediate emergency dispatch within $120\text{ minutes}$.
  4. `CRITICAL_EXPIRED` ($\le 0.2\text{ hours}$): Unsafe for human consumption; reroute to biogas/compost.

---

### 2. Mathematical Formulation

#### A. Temperature-Dependent Microbial Kinetics (Arrhenius Equation & $Q_{10}$ Rule)
The specific spoilage rate constant $k(T)$ varies with absolute temperature $T$ according to the Arrhenius relation:
$$k(T) = A \cdot \exp\left(-\frac{E_a}{R \cdot T}\right)$$
Where:
* $E_a$ = Activation energy of bacterial metabolism ($\approx 65\text{ kJ/mol}$)
* $R$ = Universal gas constant ($8.314\text{ J/(mol}\cdot\text{K)}$)
* $A$ = Pre-exponential frequency factor

For perishable cooked foods, the degradation rate approximately doubles every $10^\circ\text{C}$ rise in temperature ($Q_{10} \approx 2.0$).

#### B. Random Forest Regressor MSE Split Criterion
At each internal decision tree node $m$, the feature $j$ and threshold $t$ are selected to maximize variance reduction:
$$\Delta\text{Var}(m) = \text{Var}(y_m) - \left( \frac{N_{\text{left}}}{N_m}\text{Var}(y_{\text{left}}) + \frac{N_{\text{right}}}{N_m}\text{Var}(y_{\text{right}}) \right)$$
Where $\text{Var}(y) = \frac{1}{N}\sum_{i=1}^{N}(y_i - \bar{y})^2$.

---

### 3. Feature Space (18 Input Dimensions)

| Feature Name | Type | Description | Unit / Range |
|---|---|---|---|
| `category` | Categorical (One-Hot) | `cooked_meals`, `dairy`, `bakery`, `fresh_produce`, `packaged_goods` | 5 Binary Features |
| `food_type` | Categorical (One-Hot) | `veg`, `non_veg`, `vegan` | 3 Binary Features |
| `ambient_temp_c` | Continuous | Local room or ambient climate temperature | $15.0^\circ\text{C} - 45.0^\circ\text{C}$ |
| `humidity_percent` | Continuous | Relative environmental humidity | $25\% - 95\%$ |
| `storage_condition` | Categorical (One-Hot) | `ambient_room`, `refrigerated`, `thermal_insulated` | 3 Binary Features |
| `packaging_type` | Categorical (One-Hot) | `open_container`, `plastic_wrap`, `sealed_foil`, `airtight_vacuum` | 4 Binary Features |
| `prepared_hours_ago` | Continuous | Elapsed time since preparation/cooking | $0.5 - 24.0\text{ hours}$ |

---

### 4. Benchmark Performance Metrics (Evaluated on Held-Out Test Set)

* **$R^2$ Score (Coefficient of Determination)**: **$94.13\%$** ($0.9413$)
* **Root Mean Squared Error (RMSE)**: **$15.47\text{ hours}$** (across multi-day and hourly items)
* **Mean Absolute Error (MAE)**: **$9.74\text{ hours}$**
* **Urgency Classification Accuracy**: **$74.30\%$**
* **Inference Latency**: **$< 2\text{ ms}$** per prediction

#### Feature Importance Ranking:
1. `storage_refrigerated` (28.6%)
2. `storage_ambient_room` (13.7%)
3. `category_packaged_goods` (11.2%)
4. `category_fresh_produce` (10.1%)
5. `category_cooked_meals` (6.7%)
6. `ambient_temp_c` (6.4%)

---

### 5. College Viva Voce / Project Defense Q&A

**Q1: Why did you choose Random Forest instead of simple Linear Regression?**
> *Answer*: Food degradation is intrinsically non-linear. The interaction between high temperature ($>35^\circ\text{C}$) and high moisture causes exponential bacterial growth, which linear models cannot capture without severe underfitting. Random Forest naturally models non-linear feature interactions and prevents overfitting through bagging (bootstrap aggregating).

**Q2: How is the ML model integrated into the full-stack web application?**
> *Answer*: The model is trained using Python (`ml/train_model.py`) and serialized to a lightweight JSON weights structure (`ml/model_weights.json`). The web server runs a zero-latency JavaScript inference engine (`mlEngine.js`) that computes ensemble predictions in under $2\text{ ms}$ without needing an external Python microservice or API gateway.

**Q3: How does the dataset represent real-world food science?**
> *Answer*: The 5,000 observations are generated using microbial kinetics equations (Arrhenius rate laws and $Q_{10}$ temperature coefficients) calibrated against standard USDA & FSSAI food safety guidelines for cooked foods, dairy, and produce.

---

### 6. Running the Training Pipeline

```bash
# 1. Regenerate dataset (5,000 samples)
python3 ml/generate_dataset.py

# 2. Train the Random Forest Ensemble
python3 ml/train_model.py

# 3. Optional: Run Scikit-Learn script (if sklearn is installed)
pip install scikit-learn pandas
python3 ml/train_sklearn.py
```
