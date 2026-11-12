"""Veritabanı adresi çalışma dizininden bağımsız olmalı (PR #10 incelemesi)."""

from servisflow.repository import db


def test_varsayilan_veritabani_proje_kokunde(monkeypatch, tmp_path):
    monkeypatch.delenv(db.DB_URL_ENV, raising=False)
    monkeypatch.chdir(tmp_path)
    assert db.default_url() == f"sqlite:///{db.PROJECT_ROOT / 'servisflow.db'}"
    assert (db.PROJECT_ROOT / "pyproject.toml").exists()


def test_ortam_degiskeni_veritabani_adresini_degistirir(monkeypatch):
    monkeypatch.setenv(db.DB_URL_ENV, "sqlite://")
    assert db.default_url() == "sqlite://"
    db.make_engine().dispose()
