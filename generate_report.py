# import os
# from docx import Document
# from docx.shared import Inches, Pt, RGBColor
# from docx.enum.text import WD_ALIGN_PARAGRAPH
# from docx.enum.table import WD_TABLE_ALIGNMENT

# doc = Document()

# # Set standard page margins (1 inch)
# for section in doc.sections:
#     section.top_margin = Inches(1)
#     section.bottom_margin = Inches(1)
#     section.left_margin = Inches(1)
#     section.right_margin = Inches(1)

# def add_custom_heading(text, level):
#     h = doc.add_heading(text, level=level)
#     h.paragraph_format.space_before = Pt(12)
#     h.paragraph_format.space_after = Pt(4)
#     return h

# # --- Title Header ---
# title_p = doc.add_paragraph()
# title_run = title_p.add_run("Business Analyst Project Portfolio Report")
# title_run.font.size = Pt(20)
# title_run.font.bold = True
# title_run.font.color.rgb = RGBColor(31, 78, 121)

# subtitle_p = doc.add_paragraph()
# sub_run = subtitle_p.add_run("Late Delivery Risk Prediction & SLA Protection Engine (Proposed Architecture)\n")
# sub_run.font.size = Pt(13)
# sub_run.font.bold = True

# meta_run = subtitle_p.add_run("Dataset: Olist Brazilian E-Commerce | Validation: 3-Way Chronological Holdout")
# meta_run.font.size = Pt(10)
# meta_run.font.italic = True
# subtitle_p.paragraph_format.space_after = Pt(14)

# # --- 1. Executive Summary ---
# add_custom_heading("1. Problem Statement & Baseline Audit", level=1)
# doc.add_paragraph(
#     "Delivery delays on the Olist marketplace represent ~8.1% of all delivered orders (~6,600 out of ~96,000 orders), "
#     "but they are strongly associated with negative customer sentiment. When orders arrive late, average customer review "
#     "scores drop from 4.29 / 5.0 to 2.57 / 5.0. Furthermore, 45.2% of late orders receive a 1-star review (compared to just "
#     "6.6% for on-time deliveries), and late shipments account for 37.8% of all 1-star reviews on the platform."
# )
# doc.add_paragraph(
#     "To address this, we developed a machine learning classification pipeline to predict late deliveries using only data "
#     "available at the time of purchase. A proposed operational framework is designed to flag high-risk orders at checkout, "
#     "enabling proactive buffer days and priority dispatch workflows."
# )

# # --- 2. Model Performance & Validation ---
# add_custom_heading("2. Out-of-Time Model Performance & Operational Metrics", level=1)
# p_metrics = doc.add_paragraph()
# p_metrics.add_run("• Validation Scheme: ").bold = True
# p_metrics.add_run("Strict 3-way temporal split. Train: Sep 2016 – Apr 2018 (70%, 67,517 orders). "
#                   "Validation: Apr 2018 – Jun 2018 (15%, 14,468 orders) used for model selection. "
#                   "Test Holdout: Jun 2018 – Aug 2018 (15%, 14,469 orders) evaluated once.\n")
# p_metrics.add_run("• Out-of-Time ROC-AUC Score: ").bold = True
# p_metrics.add_run("0.7255 (evaluated on untouched holdout test period)\n")
# p_metrics.add_run("• PR-AUC (Average Precision): ").bold = True
# p_metrics.add_run("0.1198 (vs. 0.0661 baseline late rate in the test period — 1.81x lift)\n")
# p_metrics.add_run("• Top 10% Flagged Volume: ").bold = True
# p_metrics.add_run("1,446 orders flagged out of 14,469 test orders\n")
# p_metrics.add_run("• Late Orders Captured in Top 10%: ").bold = True
# p_metrics.add_run("153 orders out of 957 actual delays\n")
# p_metrics.add_run("• Top Decile Capture Rate: ").bold = True
# p_metrics.add_run("15.99% of total delays captured by reviewing only the top 10% riskiest orders\n")
# p_metrics.add_run("• Delay Risk Concentration: ").bold = True
# p_metrics.add_run("10.58% delay rate inside the flagged top decile (1.6x the baseline rate)")

# # --- 3. Root-Cause Analysis (SHAP) & Limitations ---
# add_custom_heading("3. Out-of-Time Feature Drivers (SHAP) & Analytical Limitations", level=1)
# p_shap = doc.add_paragraph()
# p_shap.add_run("1. Purchase Month: ").bold = True
# p_shap.add_run("Strongest driver in the model. Captures seasonal delay patterns and carrier bottlenecks, "
#                "though this signal is based on only ~2 years of historical data and warrants continuous monitoring as more years accumulate.\n")
# p_shap.add_run("2. Promised Delivery Windows (estimated_delivery_days): ").bold = True
# p_shap.add_run("Tight promised delivery windows are strongly associated with higher late-delivery risk, "
#                "as aggressive platform promises leave little margin for natural transit variance.\n")
# p_shap.add_run("3. Geographic Association (customer_state, seller_state, is_interstate, total_freight): ").bold = True
# p_shap.add_run("Interstate origin-destination pairs and higher freight values correlate with increased delay risk.\n")
# p_shap.add_run("4. Physical & Order Complexity: ").bold = True
# p_shap.add_run("Higher product weight, larger package volume, and multi-item/multi-seller orders exhibit modest positive association with delay probability.")

# plot_file = "data/shap_summary_plot.png"
# if os.path.exists(plot_file):
#     doc.add_paragraph().paragraph_format.space_before = Pt(8)
#     doc.add_picture(plot_file, width=Inches(5.5))
#     cap = doc.add_paragraph("Figure 1: SHAP Summary Plot — Out-of-Time Feature Associations")
#     cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
#     cap.runs[0].font.size = Pt(9)
#     cap.runs[0].font.italic = True

# # --- 4. Illustrative Cost-Benefit Scenario ---
# add_custom_heading("4. Cost-Benefit Analysis (Illustrative Scenario with Assumptions)", level=1)
# doc.add_paragraph(
#     "Note: The following financial scenario is an illustrative projection based on assumptions "
#     "(annual order volume of 50,000, $15 concession voucher per delay, and an assumed 35% delay resolution rate "
#     "via dynamic buffering and warehouse prioritization). It serves as a framework to evaluate business viability."
# )

# table_data = [
#     ["Component", "Baseline", "With Proposed SLA Engine", "Projected Net Delta"],
#     ["Annual Order Volume (Assumed)", "50,000", "50,000", "—"],
#     ["Baseline Delay Rate (Holdout Period)", "6.61% (3,305 delays)", "6.61% (3,305 delays)", "—"],
#     ["High-Risk Orders Flagged (Top 10%)", "0", "5,000", "+5,000 flagged"],
#     ["Expected Delays in Flagged Group (10.58% hit rate)", "0", "529", "+529 intercepted"],
#     ["Avoided Delays via Buffer/Routing (Assumed 35% resolution)", "0", "185", "-185 delayed orders"],
#     ["Voucher Concession Savings (@ $15/delay avoided)", "$49,575", "$46,800", "+$2,775 savings"],
#     ["Estimated GMV Retained (Assumed 50 retained accounts)", "Baseline", "+$17,500", "+$17,500 ARR"],
#     ["Cloud Infrastructure & Inference Costs (Assumed $300/mo)", "$0", "-$3,600", "-$3,600 cost"],
#     ["Net First-Year Projected Business Impact", "Baseline", "—", "+$16,675"]
# ]

# table = doc.add_table(rows=len(table_data), cols=4)
# table.alignment = WD_TABLE_ALIGNMENT.CENTER
# table.style = 'Light Shading Accent 1'

# for row_idx, row in enumerate(table_data):
#     for col_idx, text in enumerate(row):
#         cell = table.cell(row_idx, col_idx)
#         cell.text = text
#         if row_idx == 0 or row_idx == len(table_data) - 1:
#             for p in cell.paragraphs:
#                 for r in p.runs:
#                     r.font.bold = True

# doc.add_paragraph().paragraph_format.space_after = Pt(12)

# # --- 5. Proposed Engineering Specifications ---
# add_custom_heading("5. Proposed Agile Specifications (Target Architecture)", level=1)

# doc.add_heading("User Story 1: Real-Time Risk Scoring Ingestion (Proposed)", level=2)
# p_story1 = doc.add_paragraph()
# p_story1.add_run("As an ").italic = True
# p_story1.add_run("Operations Product Manager, ")
# p_story1.add_run("I want ").italic = True
# p_story1.add_run("checkout order attributes scored by the delay prediction service, ")
# p_story1.add_run("so that ").italic = True
# p_story1.add_run("high-risk shipments can be identified before carrier manifests are generated.\n")
# p_story1.add_run("Acceptance Criteria:\n").bold = True
# p_story1.add_run("1. Return delay probability within 250ms of order placement.\n")
# p_story1.add_run("2. If risk score exceeds the top-decile threshold, set sla_risk_tier = 'HIGH'.\n")
# p_story1.add_run("3. System timeout (>500ms) gracefully falls back to 'STANDARD' without blocking customer checkout.")

# doc.add_heading("User Story 2: Merchant Portal Priority Tagging (Proposed)", level=2)
# p_story2 = doc.add_paragraph()
# p_story2.add_run("As a ").italic = True
# p_story2.add_run("Marketplace Merchant, ")
# p_story2.add_run("I want ").italic = True
# p_story2.add_run("high-risk shipments highlighted on daily picking lists, ")
# p_story2.add_run("so that ").italic = True
# p_story2.add_run("time-sensitive orders can be packed and transferred to carriers promptly.\n")
# p_story2.add_run("Acceptance Criteria:\n").bold = True
# p_story2.add_run("1. Orders flagged as 'HIGH' render with a visible red 'Priority Carrier Pickup' badge.\n")
# p_story2.add_run("2. Shipping label manifests prepend 'EXP-' to carrier tracking payloads.")

# output_path = "deliverables/Olist_Project_Report.docx"
# os.makedirs("deliverables", exist_ok=True)
# doc.save(output_path)

# print(f"\nDocument updated successfully at: {output_path}")

import os
import math
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# ---------------------------------------------------------------
# Results from scripts 2 and 4 (update here; everything else derives from these)
# ---------------------------------------------------------------
M = dict(
    n_trees=300, val_auc=0.7328,
    roc_auc=0.7351, pr_auc=0.1404, base_rate=0.0661,
    flagged=1446, test_n=14469, captured=235, test_late=957,
    capture_rate=24.56, hit_rate=16.25,
)
lift_pr = M["pr_auc"] / M["base_rate"]
lift_hit = (M["hit_rate"] / 100) / M["base_rate"]

# Illustrative scenario assumptions
ORDERS, FLAG_PCT, RESOLVE, VOUCHER, GMV, CLOUD = 50_000, 0.10, 0.35, 15, 17_500, 3_600
flagged = int(ORDERS * FLAG_PCT)
base_delays = round(ORDERS * M["base_rate"])
intercepted = math.floor(flagged * M["hit_rate"] / 100 + 0.5)
avoided = math.floor(intercepted * RESOLVE)            # truncate (conservative)
base_cost = base_delays * VOUCHER
savings = avoided * VOUCHER
net = savings + GMV - CLOUD

doc = Document()
for s in doc.sections:
    s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Inches(1)

doc.styles["Normal"].font.name = "Calibri"
doc.styles["Normal"].font.size = Pt(11)

# ---------------- helpers ----------------
def heading(text, level=1):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(4)
    return h

def para(text="", space_after=6):
    p = doc.add_paragraph(text)
    p.paragraph_format.space_after = Pt(space_after)
    return p

def labeled(style, label, text):
    """One paragraph per item (real bullet / list style, bold label + body)."""
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_after = Pt(3)
    p.add_run(label).bold = True
    p.add_run(text)
    return p

def numbered(n, label, text, bold_label=True):
    """Manual numbered item with a hanging indent (no numbering carry-over between lists)."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Inches(0.3)
    pf.first_line_indent = Inches(-0.3)
    pf.space_after = Pt(3)
    pf.tab_stops.add_tab_stop(Inches(0.3))
    p.add_run(f"{n}.\t")
    if label:
        r = p.add_run(label)
        r.bold = bold_label
    p.add_run(text)
    return p

def set_cell_width(cell, inches):
    cell.width = Inches(inches)

def repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trPr.append(el)

# ---------------- title ----------------
t = doc.add_paragraph()
r = t.add_run("Business Analyst Project Portfolio Report")
r.font.size, r.font.bold, r.font.color.rgb = Pt(20), True, RGBColor(31, 78, 121)
t.paragraph_format.space_after = Pt(2)

sub = doc.add_paragraph()
r = sub.add_run("Late Delivery Risk Prediction & SLA Protection Engine (Proposed Architecture)")
r.font.size, r.font.bold = Pt(13), True
sub.paragraph_format.space_after = Pt(0)

meta = doc.add_paragraph()
r = meta.add_run("Dataset: Olist Brazilian E-Commerce | Validation: 3-Way Chronological Holdout")
r.font.size, r.font.italic = Pt(10), True
meta.paragraph_format.space_after = Pt(14)

# ---------------- 1 ----------------
heading("1. Problem Statement & Baseline Audit")
para("Delivery delays on the Olist marketplace represent ~8.1% of all delivered orders (~7,800 out of ~96,500 orders), "
     "but they are strongly associated with negative customer sentiment. When orders arrive late, average customer review "
     "scores drop from 4.29 / 5.0 to 2.57 / 5.0. Furthermore, 45.2% of late orders receive a 1-star review (compared to just "
     "6.6% for on-time deliveries), and late shipments account for 37.8% of all 1-star reviews on the platform.")
para("To address this, a machine learning classification pipeline was built to predict late deliveries using only data "
     "available at the time of purchase. A proposed operational framework would flag high-risk orders at checkout, "
     "enabling proactive buffer days and priority dispatch workflows.")

# ---------------- 2 ----------------
heading("2. Out-of-Time Model Performance & Operational Metrics")
B = "List Bullet"
labeled(B, "Validation Scheme: ",
        "Strict 3-way temporal split. Train: Sep 2016 – Apr 2018 (70%, 67,517 orders). "
        "Validation: Apr 2018 – Jun 2018 (15%, 14,468 orders) used to select the ensemble size "
        f"({M['n_trees']} trees, peak validation ROC-AUC {M['val_auc']:.4f}). "
        "Test Holdout: Jun 2018 – Aug 2018 (15%, 14,469 orders) evaluated once.")
labeled(B, "Out-of-Time ROC-AUC: ", f"{M['roc_auc']:.4f} (untouched holdout test period)")
labeled(B, "PR-AUC (Average Precision): ",
        f"{M['pr_auc']:.4f} (vs. {M['base_rate']:.4f} baseline late rate in the test period; {lift_pr:.2f}x lift)")
labeled(B, "Top 10% Flagged Volume: ", f"{M['flagged']:,} orders flagged out of {M['test_n']:,} test orders")
labeled(B, "Late Orders Captured in Top 10%: ", f"{M['captured']} orders out of {M['test_late']} actual delays")
labeled(B, "Top Decile Capture Rate: ",
        f"{M['capture_rate']:.2f}% of all delays captured by reviewing only the 10% riskiest orders")
labeled(B, "Delay Risk Concentration: ",
        f"{M['hit_rate']:.2f}% delay rate inside the flagged top decile ({lift_hit:.1f}x the baseline rate)")

# ---------------- 3 ----------------
heading("3. Out-of-Time Feature Drivers (SHAP) & Analytical Limitations")
numbered(1, "Promised Delivery Windows (estimated_delivery_days): ",
         "Strongest driver (mean |SHAP| 0.64). Tight promised delivery windows are associated with higher "
         "late-delivery risk, as aggressive promises leave little margin for natural transit variance.")
numbered(2, "Purchase Month: ",
         "Nearly tied with the top driver (0.63). Captures seasonal delay patterns, but the test window covers only "
         "June–August, so it acts largely as a seasonal baseline for that period. The signal rests on only ~2 years of "
         "history and warrants continuous monitoring as more data accumulates.")
numbered(3, "Geographic Association (customer_state, total_freight, seller_state, is_interstate): ",
         "Interstate origin-destination pairs, higher freight values, and certain destination states are associated "
         "with increased delay risk.")
numbered(4, "Physical & Order Complexity: ",
         "Product weight, package volume, item count, and seller count each have comparatively small effects "
         "(mean |SHAP| below 0.07).")

# Plot: the SHAP script saves to deliverables/, so look there first
plot_file = next((p for p in ["deliverables/shap_summary_plot.png", "data/shap_summary_plot.png"]
                  if os.path.exists(p)), None)
if plot_file:
    pic_p = doc.add_paragraph()
    pic_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pic_p.paragraph_format.space_before = Pt(8)
    pic_p.paragraph_format.keep_with_next = True
    pic_p.add_run().add_picture(plot_file, width=Inches(5.5))
    cap = doc.add_paragraph("Figure 1: SHAP Summary Plot — Out-of-Time Feature Associations")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.runs[0].font.size, cap.runs[0].font.italic = Pt(9), True
else:
    print("WARNING: SHAP plot not found; report generated without Figure 1.")

# ---------------- 4 ----------------
heading("4. Cost-Benefit Analysis (Illustrative Scenario with Assumptions)")
para(f"Note: The following financial scenario is an illustrative projection based on assumptions "
     f"(annual order volume of {ORDERS:,}, ${VOUCHER} concession voucher per delay, and an assumed {RESOLVE:.0%} delay "
     f"resolution rate via dynamic buffering and warehouse prioritization). It is not a measured result.")

rows = [
    ["Component", "Baseline", "With Proposed SLA Engine", "Projected Net Delta"],
    ["Annual Order Volume (Assumed)", f"{ORDERS:,}", f"{ORDERS:,}", "—"],
    ["Baseline Delay Rate (Holdout Period)", f"{M['base_rate']:.2%} ({base_delays:,} delays)",
     f"{M['base_rate']:.2%} ({base_delays:,} delays)", "—"],
    ["High-Risk Orders Flagged (Top 10%)", "0", f"{flagged:,}", f"+{flagged:,} flagged"],
    [f"Expected Delays in Flagged Group ({M['hit_rate']:.2f}% hit rate)", "0", f"{intercepted}", f"+{intercepted} intercepted"],
    [f"Avoided Delays via Buffer/Routing (Assumed {RESOLVE:.0%} resolution)", "0", f"{avoided}", f"-{avoided} delayed orders"],
    [f"Voucher Concession Savings (@ ${VOUCHER}/delay avoided)", f"${base_cost:,}", f"${base_cost - savings:,}", f"+${savings:,} savings"],
    ["Estimated GMV Retained (Assumed 50 retained accounts)", "Baseline", f"+${GMV:,}", f"+${GMV:,} ARR"],
    ["Cloud Infrastructure & Inference Costs (Assumed $300/mo)", "$0", f"-${CLOUD:,}", f"-${CLOUD:,} cost"],
    ["Net First-Year Projected Business Impact", "Baseline", "—", f"+${net:,}"],
]
widths = [2.7, 1.2, 1.3, 1.3]          # sums to 6.5in = text width
table = doc.add_table(rows=len(rows), cols=4)
table.style = "Table Grid"
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.autofit = False
for ci, w in enumerate(widths):
    table.columns[ci].width = Inches(w)      # also sets the grid, which Word/LibreOffice honour
for ri, row in enumerate(rows):
    for ci, text in enumerate(row):
        cell = table.cell(ri, ci)
        set_cell_width(cell, widths[ci])
        cell.text = ""
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.keep_with_next = ri < len(rows) - 1   # keep the table on one page
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if ci == 0 else WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.size = Pt(9)
        if ri == 0 or ri == len(rows) - 1:
            run.bold = True
        if ri == 0:
            tcPr = cell._tc.get_or_add_tcPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), "D9E2F3")
            tcPr.append(shd)
repeat_header(table.rows[0])
for row in table.rows:                       # never split a row across pages
    cs = OxmlElement("w:cantSplit"); cs.set(qn("w:val"), "true")
    row._tr.get_or_add_trPr().append(cs)
para("", space_after=6)

# ---------------- 5 ----------------
heading("5. Proposed Agile Specifications (Target Architecture)")

def story(title, role, want, so, criteria):
    heading(title, level=2)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    art = "an" if role[0].lower() in "aeiou" else "a"
    p.add_run(f"As {art} ").italic = True;  p.add_run(role + ", ")
    p.add_run("I want ").italic = True; p.add_run(want + ", ")
    p.add_run("so that ").italic = True; p.add_run(so + ".")
    ac = doc.add_paragraph()
    ac.paragraph_format.space_after = Pt(2)
    ac.paragraph_format.keep_with_next = True
    ac.add_run("Acceptance Criteria:").bold = True
    for i, c in enumerate(criteria, 1):
        numbered(i, "", c)

story("User Story 1: Real-Time Risk Scoring Ingestion (Proposed)",
      "Operations Product Manager",
      "checkout order attributes scored by the delay prediction service",
      "high-risk shipments can be identified before carrier manifests are generated",
      ["Return delay probability within 250ms of order placement.",
       "If risk score exceeds the top-decile threshold, set sla_risk_tier = 'HIGH'.",
       "System timeout (>500ms) gracefully falls back to 'STANDARD' without blocking customer checkout."])

story("User Story 2: Merchant Portal Priority Tagging (Proposed)",
      "Marketplace Merchant",
      "high-risk shipments highlighted on daily picking lists",
      "time-sensitive orders can be packed and transferred to carriers promptly",
      ["Orders flagged as 'HIGH' render with a visible red 'Priority Carrier Pickup' badge.",
       "Shipping label manifests prepend 'EXP-' to carrier tracking payloads."])

output_path = "deliverables/Olist_Project_Report.docx"
os.makedirs("deliverables", exist_ok=True)
doc.save(output_path)
print(f"\nDocument updated successfully at: {output_path}")