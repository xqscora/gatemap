from pathlib import Path
import shutil

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).parent
OUT = ROOT / "demo"
TARGET = OUT / "gatemap_demo_2026-09-06.webm"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900}, record_video_dir=str(OUT), record_video_size={"width": 1440, "height": 900})
        page = context.new_page()
        video = page.video
        page.goto("http://127.0.0.1:8795/", wait_until="networkidle")
        page.wait_for_timeout(900)
        page.screenshot(path=str(OUT / "gatemap_start.png"), full_page=False)
        page.get_by_role("button", name="Load example").click()
        page.get_by_role("button", name="Run GateMap").click()
        page.get_by_text("Asking Ollama locally...").wait_for(state="hidden", timeout=60000)
        assert page.get_by_text("Structured locally. No upload occurred.").is_visible()
        assert page.get_by_text("ollama-local", exact=False).is_visible()
        page.wait_for_timeout(900)
        page.screenshot(path=str(OUT / "gatemap_result.png"), full_page=False)
        with page.expect_download() as download_info:
            page.get_by_role("button", name="Export local brief").click()
        assert download_info.value.suggested_filename == "gatemap-local-brief.json"
        page.wait_for_timeout(900)
        assert page.get_by_text("Brief exported locally.").is_visible()
        page.screenshot(path=str(OUT / "gatemap_receipt.png"), full_page=False)
        page.close()
        context.close()
        source = Path(video.path())
        if source != TARGET:
            shutil.copyfile(source, TARGET)
        browser.close()
    print(f"Captured {TARGET}")


if __name__ == "__main__":
    main()
