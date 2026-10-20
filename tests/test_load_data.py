"""Degradación por dataset: un archivo ausente o ilegible no tumba el hub."""

import app


def test_load_data_skips_missing_and_corrupt(tmp_path, monkeypatch):
    """Un CSV corrupto y otro ausente se omiten; no hay excepción global."""
    corrupt = tmp_path / "corrupto.csv"
    corrupt.write_bytes(b"\xff\xfe\x00\x01dato ilegible")
    missing = tmp_path / "no-existe.csv"

    monkeypatch.setattr(app, "GAMES_CSV", corrupt)
    monkeypatch.setattr(app, "SPEECHES_CSV", missing)

    data = app.load_data()

    assert isinstance(data, dict)
    assert "games" not in data
    assert "speeches" not in data


def test_load_data_without_any_source(monkeypatch, tmp_path):
    """Sin ningún dataset en disco devuelve {} y sigue siendo usable la app."""
    for name in (
        "WC_DB",
        "GAMES_CSV",
        "SPEECHES_CSV",
        "CENSUS_CSV",
        "EVENTS_CSV",
        "PRESIDENTS_CSV",
    ):
        monkeypatch.setattr(app, name, tmp_path / f"no-existe-{name}")

    assert app.load_data() == {}
