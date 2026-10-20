"""Tests: los KPIs del overview salen de load_data(), no de cifras hardcodeadas."""

import pandas as pd

from app import (
    PROJECTS,
    get_data,
    kpi_value,
    overview_kpis,
    overview_tab,
    project_desc,
)


def test_kpis_projects_matches_index():
    assert overview_kpis()["projects"] == len(PROJECTS)


def test_kpis_derived_from_data():
    data = get_data()
    original = data.get("games")
    existed = "games" in data
    data["games"] = pd.DataFrame({"source": ["Steam"] * 5})
    try:
        assert overview_kpis()["games"] == 5
        assert "children='5'" in str(overview_tab())
        assert "150+" not in str(overview_tab())
    finally:
        if existed:
            data["games"] = original
        else:
            data.pop("games", None)


def test_kpis_none_when_dataset_missing():
    data = get_data()
    original = data.get("speeches")
    existed = "speeches" in data
    data.pop("speeches", None)
    try:
        assert overview_kpis()["speeches"] is None
        assert kpi_value(None) == "n/d"
        assert "n/d" in str(overview_tab())
    finally:
        if existed:
            data["speeches"] = original


def test_project_desc_uses_real_count():
    data = get_data()
    original = data.get("cajas")
    existed = "cajas" in data
    data["cajas"] = pd.DataFrame({"lat": [0.0] * 3, "lon": [0.0] * 3})
    try:
        cajas = next(p for p in PROJECTS if p["tab"] == "cajas")
        assert project_desc(cajas) == "3 puntos de entrega"
        sanit = next(p for p in PROJECTS if p["tab"] == "sanit")
        assert "{" not in project_desc(sanit)
    finally:
        if existed:
            data["cajas"] = original
        else:
            data.pop("cajas", None)


def test_project_desc_without_count_template():
    worldcup = next(p for p in PROJECTS if p["tab"] == "worldcup")
    assert project_desc(worldcup) == worldcup["desc"]
