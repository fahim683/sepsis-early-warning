# Project Charter: Sepsis Early Warning

| | |
|---|---|
| **Status** | Draft v0.1 (Phase 0) |
| **Owner** | Fahim Kundi |
| **Last updated** | 2026-10-13 |
| **Data** | PhysioNet/CinC Challenge 2019, training sets A and B |

> This is a learning project. The model is not a medical device, has not been
> clinically validated and must not be used for patient care.

## 1. Problem

Sepsis is a life-threatening organ dysfunction caused by a dysregulated response
to infection (Sepsis-3 definition). Every hour of delay in treatment is associated
with worse outcomes, yet sepsis is often recognized late because early signs are
subtle and spread across many vitals and labs charted at different times.

**Goal:** build a model that flags ICU patients at high risk of sepsis about
6 hours before the Sepsis-3 onset time, using only routinely collected hourly
vitals, labs and demographics. The model must also generate few enough false
alarms to be usable, and explain each alert.

## 2. Prediction task

| Element | Definition |
|---|---|
| **Population** | Adult ICU stays in PhysioNet 2019 training sets A and B (exclusions defined in Phase 2) |
| **Unit of prediction** | One patient-hour. The model scores each patient once per hour of ICU stay |
| **Inputs at hour *t*** | All 40 variables recorded at hours ≤ *t* for that patient. Nothing from after *t* |
| **Target** | `SepsisLabel` at hour *t*, used **as provided** |
| **Output** | Probability of sepsis, an alert flag (probability ≥ threshold) and the top contributing factors |

### Label and timing

The dataset defines **t_sepsis** using Sepsis-3: suspicion of infection (IV
antibiotics plus a blood culture within a set window) combined with a SOFA
increase of 2 or more points. t_sepsis is the earlier of the suspicion time and the
SOFA deterioration time.

`SepsisLabel` is **already shifted 6 hours earlier**:

- Sepsis patients: `SepsisLabel = 1` for hours *t* ≥ t_sepsis − 6, otherwise 0.
- Non-sepsis patients: `SepsisLabel = 0` for every hour.

So predicting `SepsisLabel` at hour *t* already means predicting sepsis up to
6 hours early. **We will not shift the label again.** Doing so would turn the task
into 12-hour-ahead prediction. The lead time is recorded in code as
`config.LABEL_LEAD_HOURS = 6`.

**A caveat about "clinical recognition":** t_sepsis is computed after the fact from
charted antibiotics, cultures and SOFA scores. It approximates, but is not the
same as, the moment a clinician recognized sepsis.

## 3. Data

| Item | Value |
|---|---|
| Source | [PhysioNet/CinC Challenge 2019 v1.0.0](https://physionet.org/content/challenge-2019/1.0.0/) |
| Patients | Set A: 20,336 (hospital system A) · Set B: 20,000 (hospital system B) · 40,336 total |
| Format | One pipe-delimited `.psv` file per patient, one row per ICU hour, NaN where a value was not measured (~42 MB in total) |
| Variables | 8 vital signs · 26 labs · 6 demographic/administrative · `SepsisLabel` |
| Sepsis prevalence | ~7% of patients and a much smaller share of hours (to be measured in Phase 1) |
| Privacy | De-identified, open access, no credentialing needed |
| License | CC BY 4.0. Attribution required (see [References](#10-references)) |

A third hospital system was used for the challenge's hidden test set. It is not
public, so **hospital B is our stand-in for an unseen hospital**.

## 4. Success metrics

The targets below are **provisional**. They will be revisited once the Phase 4
baseline gives us a real reference point, and any change will be recorded in the
Experiment Log.

### Primary metric

| Metric | Why | Provisional target (hospital B) |
|---|---|---|
| **Normalized challenge utility score** | Rewards early alerts, penalizes late alerts and false alarms; this is the official challenge metric | ≥ 0.30 |

The utility score gives a reward of up to +1 for alerts made from 12 hours before
t_sepsis to 3 hours after it, a penalty of up to −2 for missing sepsis, and −0.05
for each false or very early alert. It is normalized so that 0 means "never alert"
and 1 means perfect. We will use the official challenge scoring code rather than
our own version of it.

### Secondary metrics

| Metric | Level | Provisional target (hospital B) |
|---|---|---|
| AUROC | Hour | ≥ 0.80 |
| AUPRC | Hour | Report and compare against prevalence and the baseline; no absolute target, because positives are rare |
| Calibration (reliability curve, Brier score) | Hour | Calibration slope within 0.8 to 1.2 after recalibration |
| Patient-level sensitivity | Patient | ≥ 70% of sepsis patients alerted before t_sepsis |
| Median lead time (t_sepsis − first alert) | Patient | ≥ 4 hours |

### Guardrails (usability)

| Guardrail | Provisional limit |
|---|---|
| Alert burden | Report alerts per 100 patient-days at the chosen threshold. Choose the threshold so that at least 1 in 10 alerted patients goes on to develop sepsis |
| Repeated alerts | After an alert, suppress further alerts for the same patient for a set number of hours (tuned in Phase 5) |
| External generalization | Gap between hospital A validation and hospital B test results reported and explained, not hidden |

### Baselines the model must beat

1. **Logistic regression** on the same features.
2. **A qSOFA-style rule**: respiratory rate ≥ 22 and systolic BP ≤ 100. The dataset
   has no mental-status variable, so this uses only those two criteria.

## 5. Scope

### In scope

- Exploratory analysis and documentation of sets A and B.
- Patient-level splits: train/validation from hospital A, external test on hospital B.
- Time-series features computed only from current and past hours.
- Logistic regression and LightGBM models, tracked in MLflow.
- Evaluation of discrimination, calibration, utility, lead time, alert burden and subgroups.
- SHAP explanations for each alert.
- FastAPI scoring service in Docker, with CI/CD, a model registry and drift monitoring.
- Shadow-mode rollout plan, audit logging design and PHI-handling design.

### Out of scope

- Any real clinical deployment or connection to an EHR.
- Real PHI. The dataset is de-identified, so PHI controls are designed and simulated only.
- Free-text notes, medications, imaging and waveform data (not in the dataset).
- Deep sequence models (RNN or transformer) for now. These are a possible extension after Phase 5.
- Treatment recommendations. The model only flags risk.

## 6. Key design decisions

| # | Decision | Reason |
|---|---|---|
| D1 | Use `SepsisLabel` exactly as provided | It is already shifted 6 hours; shifting again would change the task |
| D2 | Train and validate on hospital A, test on hospital B | Measures generalization to a hospital the model has never seen, and gives a real drift scenario for Phase 8 |
| D3 | Split by patient, never by row | Hours from the same patient are highly correlated, and splitting by row would leak information |
| D4 | Features may only use hours ≤ *t* | The model must work in real time; enforced with truncation tests in Phase 3 |
| D5 | Missingness flags are built, then tested with and without | Whether a lab was ordered partly reflects what the clinician already suspects. This is a useful signal, but it measures clinician behaviour as well as the patient's condition |
| D6 | Primary metric is the challenge utility score; AUROC is secondary | AUROC ignores timing and alert burden, which decide whether a model is usable |
| D7 | Only the variables available in the dataset are used for subgroup checks | The dataset has age, sex, ICU unit and hospital, but no race or ethnicity, so fairness analysis will be limited, and the Model Card will say so |

## 7. Stakeholders (simulated)

| Role | Interest |
|---|---|
| ICU physicians and nurses | Early, trustworthy alerts that come with a reason and don't cause alarm fatigue |
| Sepsis / rapid-response team | Enough lead time to act on the hour-1 bundle |
| Clinical informatics | Integration, monitoring and audit trail |
| Quality and safety / governance | Evidence of safety, fairness and a controlled rollout |
| Data science (owner) | Builds, evaluates, documents and maintains the model |

## 8. Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Future data leaking into features | Results look far better than reality | Use hours ≤ *t* only, enforced by truncation tests (D4) |
| The same patient appears in two splits | Results look better than reality | Patient-level split plus tests that fail on overlap (D3) |
| Alarm fatigue | Clinicians ignore alerts | Guardrails on alert burden and suppression; threshold chosen for clinical use, not for AUROC |
| Poor results at a new hospital | Model fails after deployment | External test on hospital B; drift monitoring in Phase 8 |
| Model learns from clinician behaviour rather than physiology | Alerts arrive only after clinicians already suspect sepsis | Ablation of missingness flags (D5); lead-time analysis |
| Label noise (t_sepsis is retrospective and depends on charting) | Ceiling on achievable performance | State it as a limitation in the Model Card |
| Readers mistake the project for a clinical tool | Harm if used for care | Disclaimer in the README, charter and Model Card |

## 9. Deliverables

| Phase | Deliverable | Document |
|---|---|---|
| 0 | Repo skeleton, CI, charter | This charter |
| 1 | Download and combine the data; EDA | Data Card + data dictionary |
| 2 | Cohort, exclusions, patient-level splits | Cohort Definition |
| 3 | Time-series features with leakage tests | Feature Spec |
| 4 | Baselines and LightGBM in MLflow | Experiment Log |
| 5 | Full evaluation | Model Card |
| 6 | SHAP explanations | Explainability Guide |
| 7 | FastAPI service in Docker | API Spec |
| 8 | Registry, CI/CD, drift monitoring | Runbooks + SOPs |
| 9 | Shadow mode, audit logging, PHI design | Risk Assessment + Go-Live Plan |

Each phase is split into sub-phases where needed. Every sub-phase goes on its
own branch and is merged only after review on GitHub.

## 10. References

1. Reyna MA, Josef CS, Jeter R, et al. *Early Prediction of Sepsis From Clinical
   Data: The PhysioNet/Computing in Cardiology Challenge 2019.* Critical Care
   Medicine. 2020;48(2):210–217.
2. Goldberger AL, Amaral LAN, Glass L, et al. *PhysioBank, PhysioToolkit, and
   PhysioNet: Components of a New Research Resource for Complex Physiologic
   Signals.* Circulation. 2000;101(23):e215–e220.
3. Singer M, Deutschman CS, Seymour CW, et al. *The Third International Consensus
   Definitions for Sepsis and Septic Shock (Sepsis-3).* JAMA. 2016;315(8):801–810.
