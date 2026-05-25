import asyncio
import os
import hashlib
import httpx
from playwright.async_api import async_playwright

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
TARGET_TEXT = "Tutte le risorse risultano al momento prenotate"
URL = "https://www.bonusveicolielettrici.mase.gov.it/veicolielettriciBeneficiario/#/login"


async def get_page_text():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(URL, wait_until="networkidle", timeout=30000)
        # Aspetta che Angular carichi
        await page.wait_for_timeout(3000)
        text = await page.inner_text("body")
        await browser.close()
        return text


async def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"})


async def main():
    print("Controllo pagina MASE...")
    text = await get_page_text()

    if TARGET_TEXT in text:
        print("Avviso ancora presente — nessuna novità.")
    else:
        print("AVVISO SPARITO — invio notifica Telegram!")
        await send_telegram(
            "🚨 <b>BONUS VEICOLI ELETTRICI</b>\n\n"
            "L'avviso di risorse esaurite <b>non è più presente</b>!\n\n"
            "Accedi subito 👉 https://www.bonusveicolielettrici.mase.gov.it/veicolielettriciBeneficiario/#/login"
        )


asyncio.run(main())
