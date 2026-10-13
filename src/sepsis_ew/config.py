"""Project-wide paths and constants.

Every module reads locations from here so that nothing hard-codes a path,
and tests can point the project at a temporary directory via the
SEPSIS_EW_DATA_DIR environment variable.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = Path(os.environ.get("SEPSIS_EW_DATA_DIR", PROJECT_ROOT / "data"))
RAW_DIR = DATA_DIR / "raw"  # untouched PhysioNet .psv files
INTERIM_DIR = DATA_DIR / "interim"  # combined Parquet, one row per patient-hour
PROCESSED_DIR = DATA_DIR / "processed"  # cohort, splits, feature tables

# The two hospital systems in the PhysioNet 2019 training data. Set A is used
# for training/validation and set B is held out as an external test hospital.
HOSPITAL_SETS = ("training_setA", "training_setB")
TRAIN_HOSPITAL = "training_setA"
EXTERNAL_TEST_HOSPITAL = "training_setB"

# SepsisLabel in the source data already turns positive 6 hours before the
# Sepsis-3 onset time, so the model predicts the label as given. Recorded here
# so the lead time is documented in code, not only in the charter.
LABEL_COLUMN = "SepsisLabel"
LABEL_LEAD_HOURS = 6

RANDOM_SEED = 42
