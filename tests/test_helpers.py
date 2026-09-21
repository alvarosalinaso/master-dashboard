"""Tests for master-dashboard helpers."""

import pytest
from app import card, stat_row, COLORS


def test_card_returns_div():
    """Test card returns html.Div with correct structure."""
    result = card("Test Title", "Test content")
    assert result.__class__.__name__ == "Div"
    assert "Test Title" in str(result)
    assert "Test content" in str(result)


def test_card_with_list_children():
    """Test card with list of children."""
    children = ["child1", "child2"]
    result = card("Title", children)
    assert "child1" in str(result)
    assert "child2" in str(result)


def test_card_custom_color():
    """Test card with custom color."""
    result = card("Title", "content", color="#ff0000")
    assert "rgb(255, 0, 0)" in str(result) or "#ff0000" in str(result)


def test_stat_row_structure():
    """Test stat_row returns correct structure."""
    stats = [(100, "Label 1"), (200, "Label 2")]
    result = stat_row(stats)
    assert result.__class__.__name__ == "Div"
    assert "100" in str(result)
    assert "Label 1" in str(result)
    assert "200" in str(result)
    assert "Label 2" in str(result)


def test_stat_row_empty():
    """Test stat_row with empty list."""
    result = stat_row([])
    assert result.__class__.__name__ == "Div"


def test_colors_dict():
    """Test COLORS dict has expected keys."""
    expected_keys = {"bg", "card", "border", "accent", "gold", "text", "muted", "green", "blue"}
    assert set(COLORS.keys()) == expected_keys