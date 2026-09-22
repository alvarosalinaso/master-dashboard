"""Tests for master-dashboard tab functions."""

import pandas as pd

from app import (
    cajas_tab,
    games_tab,
    geo_tab,
    get_data,
    nlp_tab,
    overview_tab,
    sanit_tab,
    worldcup_tab,
)


def test_overview_tab():
    """Test overview_tab returns valid structure."""
    overview_tab()
    assert "Proyectos Destacados" in str(overview_tab())
    assert "7" in str(overview_tab())  # 7 projects


def test_worldcup_tab_no_data():
    """Test worldcup_tab with no data."""
    data = get_data()
    wc_backup = data.get("wc_matches")
    if "wc_matches" in data:
        del data["wc_matches"]

    result = worldcup_tab()
    assert "Data not available" in str(result)

    if wc_backup is not None:
        data["wc_matches"] = wc_backup


def test_worldcup_tab_with_data():
    """Test worldcup_tab with mock data."""

    data = get_data()
    mock_matches = pd.DataFrame(
        {
            "home_score": [2, 1, 3],
            "away_score": [1, 1, 0],
        }
    )
    data["wc_matches"] = mock_matches

    result = worldcup_tab()
    assert "Partidos" in str(result) or "Goles" in str(result)

    if "wc_matches" in get_data():
        del get_data()["wc_matches"]


def test_games_tab_no_data():
    """Test games_tab with no data."""
    data = get_data()
    if "games" in data:
        del data["games"]

    result = games_tab()
    assert "Data not available" in str(result)


def test_games_tab_with_data():
    """Test games_tab with mock data."""

    data = get_data()
    mock_games = pd.DataFrame(
        {
            "source": ["Steam", "Itch", "Steam"],
        }
    )
    data["games"] = mock_games

    result = games_tab()
    assert "Juegos" in str(result) or "Plataformas" in str(result)

    if "games" in get_data():
        del get_data()["games"]


def test_nlp_tab_no_data():
    """Test nlp_tab with no data."""
    data = get_data()
    if "speeches" in data:
        del data["speeches"]

    result = nlp_tab()
    assert "Data not available" in str(result)


def test_nlp_tab_with_data():
    """Test nlp_tab with mock data."""

    data = get_data()
    mock_speeches = pd.DataFrame(
        {
            "year": [2020, 2021, 2022],
            "speaker": ["A", "B", "C"],
        }
    )
    data["speeches"] = mock_speeches

    result = nlp_tab()
    assert "Discursos" in str(result) or "Período" in str(result)

    if "speeches" in get_data():
        del get_data()["speeches"]


def test_geo_tab_no_data():
    """Test geo_tab with no data."""
    data = get_data()
    if "census" in data:
        del data["census"]

    result = geo_tab()
    assert "Data not available" in str(result)


def test_geo_tab_with_data():
    """Test geo_tab with mock data."""

    data = get_data()
    mock_census = pd.DataFrame(
        {
            "census_year": [2010, 2015, 2020],
            "population": [1000, 1100, 1200],
            "region": ["A", "A", "A"],
        }
    )
    data["census"] = mock_census

    result = geo_tab()
    assert "Regiones" in str(result) or "Censos" in str(result)

    if "census" in get_data():
        del get_data()["census"]


def test_cajas_tab_no_data():
    """Test cajas_tab with no data."""
    data = get_data()
    if "cajas" in data:
        del data["cajas"]

    result = cajas_tab()
    assert "Data not available" in str(result)


def test_sanit_tab_no_data():
    """Test sanit_tab with no data."""
    data = get_data()
    if "sanit" in data:
        del data["sanit"]

    result = sanit_tab()
    assert "Data not available" in str(result)
