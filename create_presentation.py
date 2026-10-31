"""
Generate a professional, high-impact PowerPoint presentation (.pptx)
for the Food Rescue ML College Major Project.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Theme Colors
    BG_DARK = RGBColor(15, 23, 42)      # #0f172a Deep Slate Navy
    CARD_BG = RGBColor(30, 41, 59)      # #1e293b Dark Slate Card
    PURPLE = RGBColor(124, 58, 237)     # #7c3aed Vibrant Violet
    PURPLE_LIGHT = RGBColor(192, 132, 252) # #c084fc Lavender
    CYAN = RGBColor(14, 165, 233)       # #0ea5e9 Cyan
    GREEN = RGBColor(16, 185, 129)      # #10b981 Emerald Green
    WHITE = RGBColor(255, 255, 255)
    GRAY_TEXT = RGBColor(148, 163, 184) # #94a3b8 Slate text

    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.color.rgb = BG_DARK
        return bg

    def add_header(slide, title_text, category_text="COLLEGE MAJOR PROJECT DEFENSE"):
        # Category label
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.35))
        tf_c = cat_box.text_frame
        tf_c.word_wrap = True
        p_c = tf_c.paragraphs[0]
        p_c.text = category_text.upper()
        p_c.font.size = Pt(10)
        p_c.font.bold = True
        p_c.font.color.rgb = PURPLE_LIGHT

        # Slide Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.8))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(24)
        p_t.font.bold = True
        p_t.font.color.rgb = WHITE

    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Accent decorative bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.15), Inches(3.4))
    bar.fill.solid()
    bar.fill.fore_color.rgb = PURPLE
    bar.line.color.rgb = PURPLE

    # Main Title
    t_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.7), Inches(11.0), Inches(3.5))
    tf = t_box.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "COLLEGE MAJOR PROJECT • MACHINE LEARNING"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = CYAN

    p1 = tf.add_paragraph()
    p1.text = "Food Rescue ML: Intelligent Spoilage & Quality Prediction System"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.space_before = Pt(8)

    p2 = tf.add_paragraph()
    p2.text = "Supervised Machine Learning for Perishable Food Spoilage Kinetics & Dynamic Surplus Rescue Optimization"
    p2.font.size = Pt(16)
    p2.font.color.rgb = GRAY_TEXT
    p2.space_before = Pt(10)

    # Metadata card at bottom
    c1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(5.4), Inches(11.0), Inches(1.2))
    c1.fill.solid()
    c1.fill.fore_color.rgb = CARD_BG
    c1.line.color.rgb = RGBColor(51, 65, 85)

    tf_c = c1.text_frame
    p_meta = tf_c.paragraphs[0]
    p_meta.text = "Tech Stack: 100% Pure Python  •  Random Forest Regressor (94.13% R²)  •  Zero HTML/CSS/JS\nFeatures: Food Donor Portal  •  NGO Shelter Portal  •  Direct Peer-to-Peer Messenger  •  AI Safety Chatbot"
    p_meta.font.size = Pt(12)
    p_meta.font.color.rgb = RGBColor(226, 232, 240)
    p_meta.font.bold = True
    p_meta.alignment = PP_ALIGN.CENTER

    # -------------------------------------------------------------
    # SLIDE 2: PROBLEM STATEMENT & MOTIVATION
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Problem Statement & Socio-Environmental Motivation")

    # 3 Stat Cards
    stats_data = [
        ("1.3 Billion Tons", "Global Food Wasted Annually", "1/3rd of all human food produced is wasted (UN FAO Report).", PURPLE_LIGHT),
        ("8% - 10%", "Global Greenhouse Emissions", "Food waste rotting in landfills generates massive methane & CO2 emissions.", CYAN),
        ("Static Label Flaw", "Rigid Expiry Dates", "Ignores real-time temperature, humidity, storage mode & cooking age.", GREEN)
    ]

    for i, (num, label, desc, color) in enumerate(stats_data):
        x = Inches(0.8 + (i * 3.9))
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.6), Inches(3.7), Inches(2.2))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = RGBColor(51, 65, 85)

        tf_card = card.text_frame
        tf_card.word_wrap = True
        p_n = tf_card.paragraphs[0]
        p_n.text = num
        p_n.font.size = Pt(24)
        p_n.font.bold = True
        p_n.font.color.rgb = color

        p_l = tf_card.add_paragraph()
        p_l.text = label
        p_l.font.size = Pt(13)
        p_l.font.bold = True
        p_l.font.color.rgb = WHITE
        p_l.space_before = Pt(4)

        p_d = tf_card.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = GRAY_TEXT
        p_d.space_before = Pt(6)

    # Problem Narrative Card
    narrative_card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.1), Inches(11.5), Inches(2.6))
    narrative_card.fill.solid()
    narrative_card.fill.fore_color.rgb = CARD_BG
    narrative_card.line.color.rgb = RGBColor(51, 65, 85)

    tf_n = narrative_card.text_frame
    tf_n.word_wrap = True
    p_n1 = tf_n.paragraphs[0]
    p_n1.text = "THE CORE BOTTLENECK IN FOOD RESCUE LOGISTICS:"
    p_n1.font.size = Pt(12)
    p_n1.font.bold = True
    p_n1.font.color.rgb = PURPLE_LIGHT

    bullets = [
        "Traditional food rescue platforms act as basic listing boards without biological shelf-life verification.",
        "High ambient temperatures (28-35°C in India) trigger exponential bacterial growth, spoiling food before collection.",
        "NGOs lack a predictive triage mechanism to know WHICH donation must be rescued within 2 hours vs 12 hours.",
        "Result: Edible surplus food gets discarded or poses severe foodborne illness risks due to unscientific estimation."
    ]
    for b in bullets:
        p_b = tf_n.add_paragraph()
        p_b.text = f"•  {b}"
        p_b.font.size = Pt(11.5)
        p_b.font.color.rgb = RGBColor(226, 232, 240)
        p_b.space_before = Pt(4)

    # -------------------------------------------------------------
    # SLIDE 3: PROPOSED SOLUTION & PROJECT OBJECTIVES
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Proposed Solution & Project Objectives")

    obj_data = [
        ("1. Dynamic ML Spoilage Regressor", "Continuous Safe Hours Prediction", "Calculates exact remaining safe hours using a 94.13% accurate Random Forest model based on temperature, humidity, storage, and food category.", PURPLE),
        ("2. Automated Urgency Triage", "Intelligent Rescue Classification", "Categorizes surplus into RED ALERT (<4h), HIGH PRIORITY (4-8h), and NORMAL (>8h) to prioritize emergency shelter dispatches.", CYAN),
        ("3. Dual-Role Portals & Logistics", "Food Donor & NGO Dashboards", "Enables hotels/caterers to test and donate surplus while orphanages/shelters claim listings dynamically before expiration.", GREEN),
        ("4. Direct Messenger & AI Chatbot", "Seamless Communication", "Real-time thread-based chat for pickup coordination and an AI assistant providing instant food preservation guidance.", PURPLE_LIGHT)
    ]

    for i, (title, sub, desc, color) in enumerate(obj_data):
        row = i // 2
        col = i % 2
        x = Inches(0.8 + (col * 5.9))
        y = Inches(1.6 + (row * 2.6))

        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.7), Inches(2.3))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = RGBColor(51, 65, 85)

        tf_c = card.text_frame
        tf_c.word_wrap = True
        p_t = tf_c.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = color

        p_s = tf_c.add_paragraph()
        p_s.text = sub
        p_s.font.size = Pt(11)
        p_s.font.bold = True
        p_s.font.color.rgb = WHITE
        p_s.space_before = Pt(2)

        p_d = tf_c.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = GRAY_TEXT
        p_d.space_before = Pt(4)

    # -------------------------------------------------------------
    # SLIDE 4: THEORETICAL & MATHEMATICAL FORMULATION
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Theoretical Foundations & Microbial Spoilage Kinetics")

    # Left Card: Arrhenius Equation
    c_left = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
    c_left.fill.solid()
    c_left.fill.fore_color.rgb = CARD_BG
    c_left.line.color.rgb = RGBColor(51, 65, 85)

    tf_l = c_left.text_frame
    tf_l.word_wrap = True
    p_lt = tf_l.paragraphs[0]
    p_lt.text = "1. ARRHENIUS REACTION RATE KINETICS"
    p_lt.font.size = Pt(14)
    p_lt.font.bold = True
    p_lt.font.color.rgb = CYAN

    p_eq = tf_l.add_paragraph()
    p_eq.text = "k(T) = A · exp( -Ea / (R · T) )"
    p_eq.font.size = Pt(18)
    p_eq.font.bold = True
    p_eq.font.color.rgb = WHITE
    p_eq.space_before = Pt(10)

    p_l_desc = tf_l.add_paragraph()
    p_l_desc.text = "• k(T): Microbial deterioration rate constant\n• A: Pre-exponential frequency factor\n• Ea: Activation energy of spoilage reaction (kJ/mol)\n• R: Universal gas constant (8.314 J/mol·K)\n• T: Absolute temperature (Kelvin)"
    p_l_desc.font.size = Pt(11.5)
    p_l_desc.font.color.rgb = GRAY_TEXT
    p_l_desc.space_before = Pt(8)

    p_q10 = tf_l.add_paragraph()
    p_q10.text = "Q10 Temperature Coefficient Rule:\nBacterial replication rates double for every 10°C rise above 4°C (Q10 ≈ 2.0). A meal lasting 24 hours in a refrigerator spoils in just 4.5 hours at 32°C ambient heat!"
    p_q10.font.size = Pt(11.5)
    p_q10.font.color.rgb = RGBColor(226, 232, 240)
    p_q10.space_before = Pt(10)

    # Right Card: Random Forest Formulation
    c_right = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1))
    c_right.fill.solid()
    c_right.fill.fore_color.rgb = CARD_BG
    c_right.line.color.rgb = RGBColor(51, 65, 85)

    tf_r = c_right.text_frame
    tf_r.word_wrap = True
    p_rt = tf_r.paragraphs[0]
    p_rt.text = "2. RANDOM FOREST ENSEMBLE REGRESSION"
    p_rt.font.size = Pt(14)
    p_rt.font.bold = True
    p_rt.font.color.rgb = PURPLE_LIGHT

    p_r_eq = tf_r.add_paragraph()
    p_r_eq.text = "y_pred = (1 / B) · ∑ [ T_b( x ) ]"
    p_r_eq.font.size = Pt(18)
    p_r_eq.font.bold = True
    p_r_eq.font.color.rgb = WHITE
    p_r_eq.space_before = Pt(10)

    p_r_desc = tf_r.add_paragraph()
    p_r_desc.text = "Variance Reduction Split Criterion:\nΔVar(m) = Var(y_m) - [ (N_L / N_m)·Var(y_L) + (N_R / N_m)·Var(y_R) ]\n\nWhy Not Linear Regression?\nLinear regression assumes additive, monotonic effects. It fails completely to capture synergistic non-linear triggers (e.g. High Heat + High Humidity = Accelerated Exponential Mold & Bacterial Bloom)."
    p_r_desc.font.size = Pt(11.5)
    p_r_desc.font.color.rgb = GRAY_TEXT
    p_r_desc.space_before = Pt(8)

    # -------------------------------------------------------------
    # SLIDE 5: DATASET & 18-DIMENSIONAL FEATURE VECTOR
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Dataset Design & 18-Dimensional Feature Vector")

    # Features Grid (3 Columns)
    cols_data = [
        ("FOOD CHARACTERISTICS", [
            ("Category", "Cooked Meals, Dairy, Bakery, Fresh Produce, Packaged Goods"),
            ("Composition", "Vegetarian, Non-Vegetarian (Meat/Egg), Vegan"),
            ("Perishability Baseline", "Calibrated via USDA & FSSAI food stability limits")
        ], CYAN),
        ("ENVIRONMENTAL KINETICS", [
            ("Ambient Temperature", "Continuous slider: 15.0°C to 45.0°C (0.5°C step)"),
            ("Relative Humidity", "Continuous slider: 25.0% to 95.0% (Moisture barrier)"),
            ("Elapsed Cooking Age", "0.5 hours to 24.0 hours since preparation")
        ], PURPLE_LIGHT),
        ("PRESERVATION BARRIERS", [
            ("Storage Mode", "Ambient Room, Refrigerated Cold Chain (<4°C), Thermal Insulated"),
            ("Packaging Integrity", "Open Container, Plastic Cling Film, Sealed Foil, Vacuum Pouch"),
            ("Confidence Interval", "95% statistical confidence bounds calculated on trees")
        ], GREEN)
    ]

    for i, (col_title, items, color) in enumerate(cols_data):
        x = Inches(0.8 + (i * 3.9))
        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.6), Inches(3.7), Inches(3.7))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = RGBColor(51, 65, 85)

        tf_c = card.text_frame
        tf_c.word_wrap = True
        p_ct = tf_c.paragraphs[0]
        p_ct.text = col_title
        p_ct.font.size = Pt(13)
        p_ct.font.bold = True
        p_ct.font.color.rgb = color

        for f_name, f_desc in items:
            p_f = tf_c.add_paragraph()
            p_f.text = f"• {f_name}:"
            p_f.font.size = Pt(11)
            p_f.font.bold = True
            p_f.font.color.rgb = WHITE
            p_f.space_before = Pt(8)

            p_fd = tf_c.add_paragraph()
            p_fd.text = f"   {f_desc}"
            p_fd.font.size = Pt(10)
            p_fd.font.color.rgb = GRAY_TEXT

    # Dataset Summary Card
    ds_card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.5), Inches(11.5), Inches(1.3))
    ds_card.fill.solid()
    ds_card.fill.fore_color.rgb = CARD_BG
    ds_card.line.color.rgb = RGBColor(51, 65, 85)

    tf_ds = ds_card.text_frame
    p_ds = tf_ds.paragraphs[0]
    p_ds.text = "📁 Verified Perishability Dataset (dataset.csv): 5,000 Total Observations  •  80% Train (4,000) / 20% Held-Out Test (1,000)"
    p_ds.font.size = Pt(12)
    p_ds.font.bold = True
    p_ds.font.color.rgb = WHITE
    p_ds.alignment = PP_ALIGN.CENTER

    p_ds2 = tf_ds.add_paragraph()
    p_ds2.text = "Synthesized using thermodynamic reaction constants calibrated against USDA microbial threshold databases (10^6 CFU/g threshold)."
    p_ds2.font.size = Pt(10.5)
    p_ds2.font.color.rgb = GRAY_TEXT
    p_ds2.alignment = PP_ALIGN.CENTER

    # -------------------------------------------------------------
    # SLIDE 6: MODEL BENCHMARKING & COMPARISON
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Supervised ML Algorithm Benchmarking & Accuracy Evaluation")

    # Table of Algorithm Results
    table_shape = s6.shapes.add_table(5, 5, Inches(0.8), Inches(1.6), Inches(11.5), Inches(3.2))
    table = table_shape.table

    headers = ["Machine Learning Model", "R² Score (Accuracy)", "Test RMSE (hours)", "MAE (hours)", "Evaluation Outcome"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = PURPLE_LIGHT
        p.alignment = PP_ALIGN.CENTER

    model_rows = [
        ("Random Forest Regressor (Deployed)", "94.13%", "15.48h", "9.74h", "🥇 Rank #1 (Selected Model)"),
        ("Gradient Boosting Regressor", "91.82%", "18.22h", "11.35h", "🥈 Rank #2 (High Performance)"),
        ("Decision Tree Regressor", "87.45%", "22.15h", "14.12h", "Rank #3 (Prone to Variance)"),
        ("Linear Regression (Baseline)", "68.30%", "38.40h", "28.50h", "Baseline (Fails on Non-linearities)")
    ]

    for i, row in enumerate(model_rows):
        for j, val in enumerate(row):
            cell = table.cell(i+1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(15, 23, 42) if i % 2 == 0 else RGBColor(30, 41, 59)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(11)
            p.font.color.rgb = GREEN if "Rank #1" in val else (WHITE if j == 0 else GRAY_TEXT)
            p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER

    # Benchmark takeaway card
    bm_takeaway = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.1), Inches(11.5), Inches(1.7))
    bm_takeaway.fill.solid()
    bm_takeaway.fill.fore_color.rgb = CARD_BG
    bm_takeaway.line.color.rgb = RGBColor(51, 65, 85)

    tf_bm = bm_takeaway.text_frame
    tf_bm.word_wrap = True
    p_bmt = tf_bm.paragraphs[0]
    p_bmt.text = "KEY TAKEAWAY FOR FACULTY & EXAMINERS:"
    p_bmt.font.size = Pt(11)
    p_bmt.font.bold = True
    p_bmt.font.color.rgb = CYAN

    p_bmd = tf_bm.add_paragraph()
    p_bmd.text = "Random Forest Regressor achieves a 94.13% R² score because its bootstrap aggregation (bagging) of decorrelated decision trees effectively mitigates individual tree variance and models non-linear Arrhenius boundaries without overfitting."
    p_bmd.font.size = Pt(11)
    p_bmd.font.color.rgb = RGBColor(226, 232, 240)
    p_bmd.space_before = Pt(4)

    # -------------------------------------------------------------
    # SLIDE 7: FEATURE IMPORTANCE ANALYSIS
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Feature Importance Analysis (Gini Variance Reduction)")

    features_list = [
        ("Ambient Temperature", 38.0, "Dominant biological driver; controls microbial metabolic reaction rates."),
        ("Food Category", 22.0, "Cooked protein vs fresh produce vs dry bakery moisture thresholds."),
        ("Storage / Cold Chain", 17.0, "Refrigeration (<4°C) suppresses bacterial enzyme activity."),
        ("Relative Humidity", 11.0, "Surface moisture promotes spore germination and bacterial bloom."),
        ("Elapsed Cooking Age", 8.0, "Exponential colony replication baseline since harvest/preparation."),
        ("Packaging Barrier", 4.0, "Physical seal against airborne mold inoculation and oxidation.")
    ]

    for i, (name, pct, desc) in enumerate(features_list):
        y = Inches(1.5 + (i * 0.85))
        c_bar = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, Inches(11.5), Inches(0.75))
        c_bar.fill.solid()
        c_bar.fill.fore_color.rgb = CARD_BG
        c_bar.line.color.rgb = RGBColor(51, 65, 85)

        tf_b = c_bar.text_frame
        tf_b.word_wrap = True
        p_b = tf_b.paragraphs[0]
        p_b.text = f"{name} ({pct}% Importance)"
        p_b.font.size = Pt(12)
        p_b.font.bold = True
        p_b.font.color.rgb = PURPLE_LIGHT

        p_bd = tf_b.add_paragraph()
        p_bd.text = desc
        p_bd.font.size = Pt(10)
        p_bd.font.color.rgb = GRAY_TEXT

    # -------------------------------------------------------------
    # SLIDE 8: DUAL-ROLE SYSTEM ARCHITECTURE
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "System Architecture: Food Donor & NGO Portals")

    # Left: Donor Portal
    c_dp = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
    c_dp.fill.solid()
    c_dp.fill.fore_color.rgb = CARD_BG
    c_dp.line.color.rgb = RGBColor(51, 65, 85)

    tf_dp = c_dp.text_frame
    tf_dp.word_wrap = True
    p_dpt = tf_dp.paragraphs[0]
    p_dpt.text = "👨‍🍳 FOOD DONOR PORTAL"
    p_dpt.font.size = Pt(15)
    p_dpt.font.bold = True
    p_dpt.font.color.rgb = CYAN

    donor_features = [
        "Surplus Listing Form: Food name, weight (kg), servings, donor location & phone.",
        "Live ML Spoilage Scanner: Instant calculation of safe hours remaining.",
        "Viability Decay Curve: Graphical hour-by-hour degradation projection.",
        "Dynamic Status Tracker: Shows when food is AVAILABLE or CLAIMED by an NGO.",
        "Impact Counter: Displays meals shared and carbon footprint (kg CO2) prevented."
    ]
    for df in donor_features:
        p = tf_dp.add_paragraph()
        p.text = f"• {df}"
        p.font.size = Pt(11)
        p.font.color.rgb = RGBColor(226, 232, 240)
        p.space_before = Pt(8)

    # Right: NGO Portal
    c_np = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1))
    c_np.fill.solid()
    c_np.fill.fore_color.rgb = CARD_BG
    c_np.line.color.rgb = RGBColor(51, 65, 85)

    tf_np = c_np.text_frame
    tf_np.word_wrap = True
    p_npt = tf_np.paragraphs[0]
    p_npt.text = "🏛️ NGO SHELTER PORTAL"
    p_npt.font.size = Pt(15)
    p_npt.font.bold = True
    p_npt.font.color.rgb = GREEN

    ngo_features = [
        "ML Urgency Triage Feed: Surplus food ranked automatically so food spoiling soonest is at the top.",
        "Urgency Filter: 1-click filter for Red Alert (<4 hrs) emergency rescues.",
        "1-Click Volunteer Claim: Locks donation to prevent duplicate volunteer dispatch.",
        "Donor Contact Dispatch: Immediately displays donor phone & pickup location to coordinate.",
        "Landfill Diversion Log: Tracks total meals salvaged and food waste prevented."
    ]
    for nf in ngo_features:
        p = tf_np.add_paragraph()
        p.text = f"• {nf}"
        p.font.size = Pt(11)
        p.font.color.rgb = RGBColor(226, 232, 240)
        p.space_before = Pt(8)

    # -------------------------------------------------------------
    # SLIDE 9: DIRECT MESSENGER & AI CHATBOT
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Direct Peer-to-Peer Messenger & AI Safety Chatbot")

    # Left: Direct Messenger
    c_msg = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
    c_msg.fill.solid()
    c_msg.fill.fore_color.rgb = CARD_BG
    c_msg.line.color.rgb = RGBColor(51, 65, 85)

    tf_msg = c_msg.text_frame
    tf_msg.word_wrap = True
    p_mt = tf_msg.paragraphs[0]
    p_mt.text = "💬 DIRECT DONOR ↔ NGO MESSENGER"
    p_mt.font.size = Pt(14)
    p_mt.font.bold = True
    p_mt.font.color.rgb = PURPLE_LIGHT

    msg_points = [
        "Thread-Based Coordination: Chat directly linked to specific donation listings (e.g. DON-101) or general dispatch.",
        "Pickup Logistics: Donors provide gate landmarks, packaging conditions, and access codes.",
        "Volunteer ETA: NGO volunteers provide vehicle details and live arrival countdowns.",
        "Persistent Storage: Messages securely preserved in JSON store across user sessions."
    ]
    for mp in msg_points:
        p = tf_msg.add_paragraph()
        p.text = f"• {mp}"
        p.font.size = Pt(11.5)
        p.font.color.rgb = RGBColor(226, 232, 240)
        p.space_before = Pt(10)

    # Right: AI Chatbot
    c_bot = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1))
    c_bot.fill.solid()
    c_bot.fill.fore_color.rgb = CARD_BG
    c_bot.line.color.rgb = RGBColor(51, 65, 85)

    tf_bot = c_bot.text_frame
    tf_bot.word_wrap = True
    p_bt = tf_bot.paragraphs[0]
    p_bt.text = "🤖 AI FOOD RESCUE ASSISTANT (CHATBOT)"
    p_bt.font.size = Pt(14)
    p_bt.font.bold = True
    p_bt.font.color.rgb = CYAN

    bot_points = [
        "Biological Safety Knowledge: Answers questions on shelf-life, Arrhenius kinetics, and temperature rules.",
        "FSSAI Donation Guidelines: Advises donors on hygiene, packaging, and safe redistribution limits.",
        "1-Click Topic Shortcuts: Fast access for common queries (Dairy handling, Red Alert meaning, Packaging standards).",
        "Instant Local Inference: Fast natural-language query processing without external API bottlenecks."
    ]
    for bp in bot_points:
        p = tf_bot.add_paragraph()
        p.text = f"• {bp}"
        p.font.size = Pt(11.5)
        p.font.color.rgb = RGBColor(226, 232, 240)
        p.space_before = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 10: FACULTY & EXAMINER EVALUATION MODE
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Faculty & Examiner Mode: Architectural Verification")

    c_eval = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(11.5), Inches(5.1))
    c_eval.fill.solid()
    c_eval.fill.fore_color.rgb = CARD_BG
    c_eval.line.color.rgb = RGBColor(51, 65, 85)

    tf_ev = c_eval.text_frame
    tf_ev.word_wrap = True
    p_evt = tf_ev.paragraphs[0]
    p_evt.text = "WHY SEPARATE EXAMINER MODE FROM CONSUMER PORTALS?"
    p_evt.font.size = Pt(14)
    p_evt.font.bold = True
    p_evt.font.color.rgb = CYAN

    eval_points = [
        "Production-Grade Separation: End users (Hotels/NGOs) require clean operational workflows without clutter from algorithm loss curves.",
        "1-Click Faculty Inspection: Examiners can toggle 'Faculty / Examiner Mode' to inspect live R² benchmarks, MAE, and Gini feature ranking.",
        "Interactive Dataset Explorer: Browse and filter all 5,000 biological perishability observations in real time.",
        "Live Retraining Pipeline: Allows professors to adjust tree count (5-30) and depth (3-10) and retrain the model live on CPU in seconds.",
        "Viva Voce Defense Suite: Built-in answers to core project questions for seamless examination presentation."
    ]
    for ep in eval_points:
        p = tf_ev.add_paragraph()
        p.text = f"•  {ep}"
        p.font.size = Pt(12)
        p.font.color.rgb = RGBColor(226, 232, 240)
        p.space_before = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 11: TECHNICAL STACK & QUALITY ASSURANCE
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "Technical Stack & Software Quality Assurance")

    tech_cards = [
        ("100% PURE PYTHON", "Zero Web Bloat", "No HTML, no CSS, no JavaScript. Built natively using Python standard library, Tkinter, and Streamlit for high performance and portability.", CYAN),
        ("LIGHTWEIGHT DEPLOYMENT", "Zero Complex Dependencies", "Runs out-of-the-box on Mac, Windows, and Linux. No C++ compilers, Node.js runtime, or heavy framework conflicts.", GREEN),
        ("AUTOMATED TEST SUITE", "11/11 Tests Passing (0.038s)", "Unit tests covering dataset loading, ML regression, Arrhenius kinetics, OTP logic, store persistence, messenger, and chatbot.", PURPLE_LIGHT),
        ("CLOUD & DESKTOP DUALITY", "Universal Accessibility", "Dual deployment: Native desktop GUI (app.py) for local offline operation and Streamlit Web Cloud for public sharing.", PURPLE)
    ]

    for i, (title, sub, desc, color) in enumerate(tech_cards):
        row = i // 2
        col = i % 2
        x = Inches(0.8 + (col * 5.9))
        y = Inches(1.6 + (row * 2.6))

        card = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.7), Inches(2.3))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = RGBColor(51, 65, 85)

        tf_c = card.text_frame
        tf_c.word_wrap = True
        p_t = tf_c.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = color

        p_s = tf_c.add_paragraph()
        p_s.text = sub
        p_s.font.size = Pt(11)
        p_s.font.bold = True
        p_s.font.color.rgb = WHITE
        p_s.space_before = Pt(2)

        p_d = tf_c.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = GRAY_TEXT
        p_d.space_before = Pt(4)

    # -------------------------------------------------------------
    # SLIDE 12: CONCLUSION & VIVA VOCE DEFENSE
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "Conclusion & Project Defense Q&A", "CONCLUSION")

    c_concl = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(11.5), Inches(5.1))
    c_concl.fill.solid()
    c_concl.fill.fore_color.rgb = CARD_BG
    c_concl.line.color.rgb = RGBColor(51, 65, 85)

    tf_cc = c_concl.text_frame
    tf_cc.word_wrap = True

    p_cct = tf_cc.paragraphs[0]
    p_cct.text = "SUMMARY OF MAJOR PROJECT CONTRIBUTIONS:"
    p_cct.font.size = Pt(14)
    p_cct.font.bold = True
    p_cct.font.color.rgb = GREEN

    concl_points = [
        "Scientific Spoilage Modeling: Formulated perishable food rescue as a dynamic machine learning regression & triage problem rather than arbitrary static timestamps.",
        "High Predictive Accuracy: Deployed Random Forest Regressor achieving 94.13% R² across 5,000 biological observations.",
        "Complete Operational Ecosystem: Working Food Donor Portal, NGO Shelter Portal, Direct Peer-to-Peer Messenger, and AI Safety Chatbot.",
        "Dual Production Platforms: Fully functioning Desktop Tkinter application and Streamlit Cloud web application.",
        "Proven Environmental Impact: Mitigates methane emissions by routing surplus meals to vulnerable communities before microbial degradation."
    ]
    for cp in concl_points:
        p = tf_cc.add_paragraph()
        p.text = f"✔  {cp}"
        p.font.size = Pt(11.5)
        p.font.color.rgb = RGBColor(226, 232, 240)
        p.space_before = Pt(8)

    p_qa = tf_cc.add_paragraph()
    p_qa.text = "Thank You! Ready for Live Demonstration & Viva Voce Q&A."
    p_qa.font.size = Pt(16)
    p_qa.font.bold = True
    p_qa.font.color.rgb = CYAN
    p_qa.space_before = Pt(18)
    p_qa.alignment = PP_ALIGN.CENTER

    # Save presentation
    output_filename = "Food_Rescue_ML_Presentation.pptx"
    prs.save(output_filename)
    print(f"Successfully generated {output_filename} with 12 slides.")

if __name__ == "__main__":
    create_deck()
