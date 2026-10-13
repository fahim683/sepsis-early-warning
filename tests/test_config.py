import importlib

import sepsis_ew
from sepsis_ew import config


def test_package_has_version():
    assert sepsis_ew.__version__


def test_data_dirs_live_under_data_dir():
    for path in (config.RAW_DIR, config.INTERIM_DIR, config.PROCESSED_DIR):
        assert path.parent == config.DATA_DIR


def test_train_and_external_test_hospitals_differ():
    assert config.TRAIN_HOSPITAL in config.HOSPITAL_SETS
    assert config.EXTERNAL_TEST_HOSPITAL in config.HOSPITAL_SETS
    assert config.TRAIN_HOSPITAL != config.EXTERNAL_TEST_HOSPITAL


def test_data_dir_can_be_overridden(monkeypatch, tmp_path):
    monkeypatch.setenv("SEPSIS_EW_DATA_DIR", str(tmp_path))
    reloaded = importlib.reload(config)
    try:
        assert reloaded.DATA_DIR == tmp_path
        assert reloaded.RAW_DIR == tmp_path / "raw"
    finally:
        monkeypatch.delenv("SEPSIS_EW_DATA_DIR")
        importlib.reload(config)
