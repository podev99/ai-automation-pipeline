import os
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv
from google import genai
from google.genai import types
import schedule

from rss_parser import fetch_latest_entry
from storage import load_seen_articles, save_seen_article
from telegram_notifier import send_telegram_message

# Load environment variables
load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP Request Handler for Render Free Tier Web Service health check."""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK - AI Automation Pipeline is Running!")


def start_health_check_server() -> None:
    """Starts a lightweight HTTP server on the port assigned by Render."""
    port = int(os.getenv("PORT", 8080))
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print(f"[HTTP Server] Health check server running on port {port}")
    httpd.serve_forever()


def summarize_article(title: str, summary: str) -> str:
    """Summarizes an article with retry delay and valid fallback models."""
    prompt = (
        f"Summarize the following tech news article into 2 clear bullet points in English.\n\n"
        f"Title: {title}\n"
        f"Content: {summary}"
    )

    config = types.GenerateContentConfig(
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        )
    )

    models_to_try = [
        "gemini-3.8-flash",
        "gemini-3.5-flash",
        "gemini-flash-latest",
    ]

    for model_name in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name, contents=prompt, config=config
                )
                return response.text.strip()
            except Exception as e:
                print(
                    f"Warning: Model {model_name} attempt {attempt + 1} failed: {e}"
                )
                time.sleep(2)

    raise RuntimeError("All Gemini models failed to process the request.")


def run_pipeline() -> None:
    """Executes the RSS -> Gemini -> Telegram automation pipeline with deduplication."""
    rss_url = "https://news.ycombinator.com/rss"
    print("\n[Scheduler] Fetching latest RSS entry...")
    entry = fetch_latest_entry(rss_url)

    if not entry:
        print("[Scheduler] No RSS entry found.")
        return

    # Check for duplicate entry
    seen_articles = load_seen_articles()
    if entry["link"] in seen_articles:
        print(f"[Scheduler] Article already processed, skipping: {entry['title']}")
        return

    print(f"[Scheduler] Processing new article: {entry['title']}")
    ai_summary = summarize_article(entry["title"], entry["summary"])

    # Format Telegram HTML message
    telegram_msg = (
        f"**📰 {entry['title']}**\n\n"
        f"{ai_summary}\n\n"
        f"🔗 [Read Full Article]({entry})"
    )

    print("[Scheduler] Sending report to Telegram...")
    success = send_telegram_message(telegram_msg)

    if success:
        save_seen_article(entry["link"])
        print("[Scheduler] Pipeline executed successfully and link saved!")
    else:
        print("[Scheduler] Failed to deliver Telegram message.")


if __name__ == "__main__":
    # Start health check HTTP server in a background thread for Render Web Service
    http_thread = threading.Thread(target=start_health_check_server, daemon=True)
    http_thread.start()

    print("=== Starting RSS Automation Pipeline Service ===")

    # Run once immediately on start
    run_pipeline()

    # Schedule task every 15 minutes
    schedule.every(15).minutes.do(run_pipeline)
    print("Scheduler initialized. Checking every 15 minutes. Press Ctrl+C to stop.")

    while True:
        schedule.run_pending()
        time.sleep(1)