"""Green v0.5 UI recovery contracts: ensure no v0.6 frontend is loaded."""
from pathlib import Path

from fastapi.testclient import TestClient
from app.main import app

ROOT = Path(__file__).resolve().parents[2]

def test_classic_green_theme_restored():
    css = (ROOT / "apps/web/styles.css").read_text(encoding="utf8")
    assert "--green:#1e5747" in css
    assert "--paper:#f7f8f5" in css
    assert "--bright:#e6f1ea" in css
    assert ".workspace-grid" in css
    assert ".mode.selected" in css
    assert "--sidebar:#121d33" not in css

def test_original_green_markup_is_active():
    html = (ROOT / "apps/web/index.html").read_text(encoding="utf8")
    assert 'content="#174938"' in html
    assert "SIMULATION · v0.5" in html
    assert '<span class="brand-mark">∴</span>' in html
    assert 'src="/assets/app.js" defer' in html
    assert 'src="/assets/studio.js"' not in html
    assert 'id="commandPalette"' not in html
    for marker in ('id="problemSelect"', 'id="studentInput"', 'id="chat"',
                   'id="thinkingStage"', 'id="methodList"', 'id="reviewList"',
                   'id="historyList"'):
        assert html.count(marker) == 1

def test_restoration_keeps_tutor_service_and_three_modes(tmp_path,monkeypatch):
    monkeypatch.setenv("STEM_MENTOR_DB",str(tmp_path/"green-restore.sqlite3"))
    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        c=client.get("/api/catalog").json()
        assert len(c["problems"]) >= 15
        assert len(c["methods"]) >= 26
        assert {m["value"] for m in c["modes"]} == {"ANALYZE","GUIDE","INDEPENDENT"}
        assert client.get("/health").json()["llm_api_used"] is False
        assert client.get("/assets/studio.js").status_code == 404
