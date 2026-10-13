# Sepsis Early Warning

Predicts sepsis about 6 hours before clinical recognition from hourly ICU vitals and
labs, using the de-identified [PhysioNet/Computing in Cardiology Challenge 2019](https://physionet.org/content/challenge-2019/1.0.0/)
dataset (~40,000 ICU stays from two hospital systems).

> Learning project. Not a medical device and not validated for clinical use.

## Roadmap

| Phase | Scope | Doc |
|---|---|---|
| 0 | Framing, repo setup, CI | [Project Charter](docs/00-project-charter.md) |
| 1 | Data understanding | Data Card + data dictionary |
| 2 | Cohort and labels, patient-level split | Cohort Definition |
| 3 | Time-series features | Feature Spec |
| 4 | Baseline + LightGBM, MLflow | Experiment Log |
| 5 | Evaluation, calibration, alert burden, subgroups | Model Card |
| 6 | SHAP explanations | Explainability Guide |
| 7 | FastAPI serving, Docker | API Spec |
| 8 | Model registry, CI/CD, drift monitoring | Runbooks + SOPs |
| 9 | Shadow mode, audit logging, PHI handling | Risk Assessment + Go-Live Plan |

All documentation lives in [docs/](docs/).

## Setup

Requires Python 3.11+.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Checks (same as CI)

```bash
ruff check src/ tests/
black --check src/ tests/
mypy src/ tests/
pytest
```

## Layout

```
src/sepsis_ew/   package code (config.py holds all paths and constants)
tests/           pytest suite
notebooks/       exploratory notebooks
docs/            phase documentation
data/            downloaded and derived data (git-ignored)
```
