# Late Delivery Risk Prediction & SLA Protection Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Database SQLite](https://img.shields.io/badge/database-SQLite-lightgrey.svg)](https://www.sqlite.org/)
[![Model LightGBM](https://img.shields.io/badge/model-LightGBM-brightgreen.svg)](https://lightgbm.readthedocs.io/)
[![Dataset Kaggle](https://img.shields.io/badge/Kaggle-Olist%20Dataset-20BEFF.svg)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

A production-grade Business Analytics & Applied Machine Learning project built on the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (~96.5K delivered orders).

This repository bridges technical data engineering, leak-free temporal machine learning validation, and business translation. It quantifies the customer satisfaction impact of fulfillment failures, constructs an early-warning dispatch risk model, validates performance on a chronological holdout, and delivers concrete Agile specifications and an illustrative Cost-Benefit Analysis for operational deployment.

---

## Executive Summary

* **The Problem:** Late deliveries make up **~8.1%** of total marketplace order volume, but they trigger severe customer friction. When an order arrives late, the average review score drops from **4.29 / 5.0 to 2.57 / 5.0**. In addition, **45.2% of late orders receive a 1-star review** (vs. 6.6% on-time), accounting for **37.8% of all 1-star reviews** platform-wide.
* **The Solution:** A predictive machine learning engine evaluated at checkout time to flag high-risk orders *before* carrier pick-up manifests are generated, enabling dynamic SLA buffering and merchant queue prioritization.
* **Methodological Rigor:** Standard random-split leakage and test-set data snooping were prevented through an indexed SQLite relational feature pipeline and a **strict 3-way chronological split** (Train 70% / Validation 15% / Test 15%). The tree ensemble size was tuned exclusively against the validation set prior to a single, final evaluation on the out-of-time test holdout.
* **Key Performance:** The chosen 300-tree LightGBM model achieved an out-of-time **ROC-AUC of 0.7351** and a **PR-AUC of 0.1404** (a **2.12× lift** over the test baseline rate). In an operational top-decile intervention scenario, the model captured **24.56% of all late deliveries** at an internal delay concentration of **16.25%** (a **2.5× risk concentration** over baseline).

---

## Business Problem & Baseline Audit

Marketplace orders with delivery status and review scores were analyzed using deduplicated SQL queries to evaluate the operational impact of delivery failures:

| Fulfillment Status | Total Delivered Orders | Volume Share | Mean Review Score (CSAT) | 1-Star Review Rate | Platform 1-Star Share |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **On-Time** | 88,644 | 91.89% | **4.29 / 5.0** | 6.58% | 62.17% |
| **Late** | 7,826 | 8.11% | **2.57 / 5.0** | **45.27%** | **37.83%** |

Delays are strongly associated with customer churn risk and negative platform perception. Rather than issuing reactive concessions ($15 refund vouchers) after delivery failures occur, proactive intervention at order placement helps protect customer lifetime value (LTV) and reduce customer support volume.

---

## Data Architecture & Pipeline

The pipeline is organized into modular Python scripts orchestrated by a master runner:

```
├── data/                                 # Raw CSVs & cached features (.gitkeep tracked)
├── deliverables/                         # Generated outputs and reports (.gitkeep tracked)
├── 1_load_db.py                          # Ingests CSVs into indexed SQLite database
├── 2_audit_baseline.py                   # Deduplicated SQL baseline & geographic bottleneck audit
├── 3_feature_engineering.py              # Window-function SQL feature pipeline
├── 4_train_model.py                      # 3-way temporal split & validation tuning pipeline
├── 5_shap_analysis.py                    # Out-of-time TreeExplainer & feature attribution
├── run_pipeline.py                       # Master orchestrator & auto-dependency resolver
├── run_pipeline.bat                      # Optional Windows double-click shortcut
├── requirements.txt                      # Reproducible library dependencies
├── .gitignore                            # Production gitignore (excludes db, caches, CSVs)
└── README.md
```

### 1. Leakage-Free Feature Engineering (`3_feature_engineering.py`)
All 14 features use data strictly known at purchase completion:
* **Deterministic Primary Seller Selection:** Uses `ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY COUNT(*) DESC, SUM(price) DESC)` to resolve the primary seller state deterministically for multi-item orders.
* **Logistics & Routing:** `is_interstate` (seller state $\ne$ customer destination state), `total_freight`, `freight_to_price_ratio`.
* **Platform Transit Window:** `estimated_delivery_days` (the promised calendar delivery window calculated at checkout).
* **Physical Package Bulk:** Average item weight (`avg_product_weight_g`) and cubic dimensions (`avg_product_volume_cm3`).
* **Cart Complexity:** `total_items`, `total_sellers`, `total_order_value`.
* **Temporal Indicators:** `purchase_month`, `purchase_dayofweek`, `purchase_hour`.

---

## Model Training & Out-of-Time Validation

### Chronological 3-Way Split Structure
To simulate real-world production performance and avoid cross-temporal data leakage:
* **Train Set (70% | 67,517 orders):** September 15, 2016 – April 15, 2018 (Baseline late rate: 9.03%)
* **Validation Set (15% | 14,468 orders):** April 15, 2018 – June 21, 2018 (Baseline late rate: 5.34%)
* **Test Holdout (15% | 14,469 orders):** June 21, 2018 – August 29, 2018 (Baseline late rate: 6.61%)

### Hyperparameter Tuning on Validation Holdout
To prevent test-set overfitting, candidate ensemble sizes were tuned strictly on the validation set using `ROC-AUC`:

| Candidate Trees | Validation ROC-AUC | Status |
| :---: | :---: | :---: |
| 50 | 0.7256 | Evaluated |
| 100 | 0.7316 | Evaluated |
| 150 | 0.7327 | Evaluated |
| 200 | 0.7320 | Evaluated |
| 250 | 0.7326 | Evaluated |
| **300** | **0.7328** | **Selected Optimal Ensemble** |

### Final Out-of-Time Holdout Evaluation
The 300-tree model was scored a single time on the untouched test holdout:

* **ROC-AUC Score:** `0.7351`
* **PR-AUC (Average Precision):** `0.1404` (vs. naive holdout baseline of `0.0661` — a **2.12× lift**)
* **Top 10% Flagged Volume:** 1,446 orders out of 14,469 holdout orders
* **Delays Captured in Top 10%:** 235 orders out of 957 total delays
* **Top Decile Capture Rate:** **24.56%**
* **Delay Risk Concentration:** **16.25%** (a **2.5× concentration** over the 6.61% baseline rate)

---

## Explainability & Root-Cause Analysis (SHAP)

SHAP (`TreeExplainer`) feature attributions were calculated on a 2,000-order sample from the out-of-time test holdout (`5_shap_analysis.py`). The table below outlines all 14 engineered features ranked by global importance:

| Rank | Feature | Mean Absolute SHAP | Directional Effect on Delay Risk |
| :---: | :--- | :---: | :--- |
| 1 | `estimated_delivery_days` | **0.6388** | Shorter promised delivery windows correlate strongly with higher delay probability; longer promises absorb transit variance. |
| 2 | `purchase_month` | **0.6261** | Reflects macro-seasonal transit variance across the historical baseline period. |
| 3 | `customer_state` | **0.3485** | Destination states with weaker infrastructure (e.g., North/Northeast hubs like MA, CE, BA) show higher delay risk. |
| 4 | `total_freight` | **0.1765** | High freight values correlate with long-haul, remote routing bottlenecks. |
| 5 | `seller_state` | **0.1252** | Dispatches from secondary merchant clusters outside major logistics hubs (SP/RJ) correlate with line-haul dwell time. |
| 6 | `is_interstate` | **0.0752** | Cross-state dispatches introduce handoff stages and multi-hub transfers compared to intrastate deliveries. |
| 7 | `total_items` | **0.0672** | Multi-item carts add picking, packing, and consolidation friction at fulfillment centers. |
| 8 | `avg_product_volume_cm3` | **0.0439** | Bulky parcels require specialized freight handling, increasing transit dwell risk. |
| 9 | `purchase_dayofweek` | **0.0403** | Late-week purchases (Thursday/Friday) face weekend depot dwelling before long-haul dispatch. |
| 10 | `avg_product_weight_g` | **0.0399** | Heavy freight experiences slower line-haul consolidation and manual handling delays. |
| 11 | `total_order_value` | **0.0395** | High-value orders often correlate with complex items requiring enhanced carrier custody checks. |
| 12 | `total_sellers` | **0.0385** | Split shipments from distinct merchant warehouses increase order fragmentation risk. |
| 13 | `freight_to_price_ratio` | **0.0348** | Unfavorable freight economics reflect inefficient or highly distant carrier routes. |
| 14 | `purchase_hour` | **0.0263** | Orders completed after carrier cutoff times face same-day manifest misses. |

---

## Business Impact: Illustrative Cost-Benefit Scenario

*Disclaimer: The following financial projection is an illustrative planning scenario based on stated operational assumptions (50,000 annualized orders, $15 concession vouchers, and an assumed 35% delay resolution rate). It provides a structured business framework for evaluating proactive SLA interventions.*

| Financial & Operational Metric | Baseline Operations | With Proposed Predictive SLA Engine | Net Delta |
| :--- | :--- | :--- | :--- |
| **Annual Order Volume (Assumed)** | 50,000 | 50,000 | — |
| **Baseline Delay Rate (Holdout Period)** | 6.61% (3,305 delays) | 6.61% (3,305 delays) | — |
| **High-Risk Orders Flagged (Top 10%)** | 0 | 5,000 | +5,000 flagged |
| **Expected Delays in Flagged Group (16.25% hit rate)**| 0 | 813 | +813 intercepted |
| **Avoided Delays via Buffer/Routing (35% resolution)** | 0 | 284 | **-284 late orders** |
| **Voucher Concession Savings (@ $15/delay avoided)** | $49,575 | $45,315 | **+$4,260** |
| **Estimated Retained GMV (Assumed 50 retained accounts)**| Baseline | +$17,500 | **+$17,500 ARR** |
| **Cloud Hosting & Inference Costs (Assumed $300/mo)** | $0 | -$3,600 | **-$3,600** |
| **Projected Net First-Year Business Impact** | Baseline | — | **+$18,160** |

---

## Proposed Agile Engineering Specifications

### User Story 1: Real-Time Risk Scoring Ingestion (Proposed)
* **As an** Operations Product Manager,
* **I want** checkout order telemetry scored by the delay prediction service,
* **So that** high-risk shipments can be identified before carrier manifests are generated.
* **Acceptance Criteria:**
  1. Return delay probability within 250ms of order placement.
  2. If the risk score exceeds the top-decile threshold, assign `sla_risk_tier = 'HIGH'`.
  3. System timeout (>500ms) gracefully falls back to `sla_risk_tier = 'STANDARD'` without interrupting customer checkout.

### User Story 2: Merchant Portal Priority Tagging (Proposed)
* **As a** Marketplace Merchant,
* **I want** high-risk shipments highlighted on daily picking lists,
* **So that** time-sensitive orders can be packed and transferred to carriers promptly.
* **Acceptance Criteria:**
  1. Orders marked `sla_risk_tier = 'HIGH'` render with a visible red "Priority Carrier Pickup" badge.
  2. Carrier shipping manifests prepend the prefix `EXP-` to tracking payloads for high-risk parcels.

---

## Quickstart & Reproducibility

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/olist-delivery-risk-engine.git
cd olist-delivery-risk-engine
```

### 2. Download the Dataset
1. Download the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) from Kaggle.
2. Extract the uncompressed `.csv` files directly into the `data/` folder:
   ```
   data/
   ├── olist_customers_dataset.csv
   ├── olist_geolocation_dataset.csv
   ├── olist_order_items_dataset.csv
   ├── olist_order_payments_dataset.csv
   ├── olist_order_reviews_dataset.csv
   ├── olist_orders_dataset.csv
   ├── olist_products_dataset.csv
   ├── olist_sellers_dataset.csv
   └── product_category_name_translation.csv
   ```

### 3. Run the Complete Pipeline
Run the master orchestrator in your terminal (no Conda required):

```bash
python run_pipeline.py
```

*What `run_pipeline.py` executes automatically:*
1. **Dependency Resolution:** Verifies `requirements.txt` and installs any missing libraries using `pip`.
2. **Database Ingestion (`1_load_db.py`):** Loads the raw CSVs into an indexed SQLite database (`olist.db`).
3. **Baseline Business Audit (`2_audit_baseline.py`):** Generates deduplicated CSAT impact and destination bottleneck audits.
4. **Feature Engineering (`3_feature_engineering.py`):** Builds SQL window-function views and outputs `data/training_features.csv`.
5. **Model Tuning & Evaluation (`4_train_model.py`):** Performs a chronological 3-way split, tunes tree counts on the validation set, and scores the holdout test set.
6. **Explainability (`5_shap_analysis.py`):** Computes out-of-time TreeExplainer SHAP values and outputs feature attribution metrics.

*(On Windows, you can also double-click `run_pipeline.bat` to launch the execution in a terminal window.)*

---

## License
This project is open-source and available under the [MIT License](LICENSE).