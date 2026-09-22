"""Dev launcher on port 8090 (avoids clashing with Docker :8050)."""
from app import app

if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8090)
