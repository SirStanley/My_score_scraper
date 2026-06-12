from playwright.sync_api import sync_playwright
import requests
import time
from datetime import datetime, timedelta


URL_PHP = "https://worldbetapp.cba.pl/auto_fetch_results.php"


def scraper():
    dzisiaj = datetime.now().strftime("%d.%m.")
    wczoraj = (datetime.now() - timedelta(days=1)).strftime("%d.%m.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"Pobieranie wyników dla: {dzisiaj} oraz {wczoraj}")
        page.goto("https://www.flashscore.pl/pilka-nozna/swiat/mistrzostwa-swiata/wyniki/")

        # RODO
        try:
            page.wait_for_selector("#onetrust-accept-btn-handler", timeout=5000)
            page.click("#onetrust-accept-btn-handler")
        except:
            pass

        page.wait_for_selector(".leagues--static")

        # Znajdź główną sekcję "ŚWIAT: Mistrzostwa Świata"
        bloki = page.query_selector_all(".leagues--static")
        target_blok = None
        for blok in bloki:
            tytul = blok.query_selector(".headerLeague__title-text")
            kat = blok.query_selector(".headerLeague__category-text")
            if tytul and kat and tytul.inner_text().strip() == "Mistrzostwa Świata" and kat.inner_text().strip() == "ŚWIAT":
                target_blok = blok
                break

        if not target_blok:
            print("Nie znaleziono sekcji głównej!")
            return

        mecze = target_blok.query_selector_all(".event__match")
        mecz_data_list = []

        # 1. Zbieranie danych
        for mecz in mecze:
            time_el = mecz.query_selector(".event__time")
            if not time_el: continue

            data_meczu = time_el.inner_text().split(' ')[0]

            if data_meczu in [dzisiaj, wczoraj]:
                h_score = mecz.query_selector(".event__score--home").inner_text().strip()
                a_score = mecz.query_selector(".event__score--away").inner_text().strip()
                home = mecz.query_selector(".event__homeParticipant .wcl-name_jjfMf").inner_text().strip()
                away = mecz.query_selector(".event__awayParticipant .wcl-name_jjfMf").inner_text().strip()
                m_id = mecz.get_attribute("id").split("_")[-1]

                mecz_data_list.append({
                    'home': home, 'away': away, 'h_score': h_score, 'a_score': a_score,
                    'url': f"https://www.flashscore.pl/mecz/{m_id}/#szczegoly-meczu"
                })

        # 2. Wysyłka do PHP
        print(f"Znaleziono {len(mecz_data_list)} mecze. Wysyłam...")

        for mecz in mecz_data_list:
            page.goto(mecz['url'])
            try:
                page.wait_for_selector(".smv__participantRow", timeout=8000)
                wiersze = page.query_selector_all(".smv__participantRow")
                strzelcy = [w.query_selector(".smv__playerName").inner_text().strip()
                            for w in wiersze if w.query_selector("[data-testid*='goal']")]

                mecz['scorers'] = ",".join(strzelcy)

                # WYSYŁKA
                response = requests.post(URL_PHP, data=mecz, timeout=10)
                print(f"Wysłano: {mecz['home']} - {mecz['away']} | Status: {response.status_code}")

            except Exception as e:
                print(f"Błąd wysyłki {mecz['home']}: {e}")

            time.sleep(1)

        browser.close()
        print("Gotowe!")


if __name__ == "__main__":
    scraper()
