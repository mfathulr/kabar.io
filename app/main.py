from __future__ import annotations

try:
    from dashboard import main
except ImportError:  # pragma: no cover - package-style fallback
    from app.dashboard import main


if __name__ == "__main__":
    main()
