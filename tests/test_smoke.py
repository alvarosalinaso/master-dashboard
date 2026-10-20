"""Test de humo: la app importa, construye su layout y responde sin error."""

import json

import app


def test_app_imports():
    assert app.server is not None
    assert app.app.layout is not None


def test_server_serves_home_and_callbacks():
    client = app.server.test_client()
    assert client.get("/").status_code == 200

    deps = client.get("/_dash-dependencies")
    assert deps.status_code == 200
    outputs = [d["output"] for d in json.loads(deps.data)]
    assert "tabs.value" in outputs
    # Superficie de callbacks: render de tabs + navegación por tarjeta + 4 de clic
    # informativo (ninguno filtra datos). Cambiar esto debería ser decisión consciente.
    assert len(outputs) == 6


def test_layout_lists_all_tabs():
    layout = str(app.app.layout)
    for value in ("overview", "worldcup", "games", "nlp", "geo"):
        assert value in layout


def test_no_promise_of_crossfilter_in_overview():
    html_out = str(app.overview_tab())
    assert "clic para filtrar" not in html_out
    assert "cross-filtering" not in html_out
