from playwright.sync_api import sync_playwright
import time
import requests
import logging

# Konfiguracja logowania 
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

URL_PHP = "https://worldbetapp.cba.pl/auto_fetch_results.php"

def scraper():
    logging.info("Rozpoczęto proces scrapowania.")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        logging.info("Ładuję stronę Flashscore...")
        page.goto("https://www.flashscore.pl/pilka-nozna/swiat/mistrzostwa-swiata/#/SbLsX4y7/tabela/")
        
        try:
            page.wait_for_selector(".event__match", timeout=15000)
        except Exception as e:
            logging.error("Nie znaleziono listy meczów (timeout).")
            return

        mecze_elements = page.query_selector_all(".event__match")
        mlodziezowki = ["U17", "U18", "U19", "U20", "U21", "U23"]
        mecz_info_list = []

        for mecz in mecze_elements:
            tekst = mecz.inner_text().split('\n')
            if len(tekst) < 5: continue
            
            home, away = tekst[1], tekst[2]
            status = tekst[0]

            if "Koniec" in status:
                if not any(wiek in home or wiek in away for wiek in mlodziezowki):
                    m_id = mecz.get_attribute("id").split("_")[-1]
                    mecz_info_list.append({
                        'home': home, 'away': away,
                        'h_score': tekst[3], 'a_score': tekst[4],
                        'url': f"https://www.flashscore.pl/mecz/{m_id}/#szczegoly-meczu"
                    })

        logging.info(f"Znaleziono {len(mecz_info_list)} meczów do przetworzenia.")

        for mecz in mecz_info_list:
            try:
                page.goto(mecz['url'], wait_until="networkidle")
                page.wait_for_selector(".smv__participantRow", timeout=15000)
                
                wiersze = page.query_selector_all(".smv__participantRow")
                strzelcy = []
                for wiersz in wiersze:
                    if wiersz.query_selector("[data-testid*='goal']"):
                        nazwisko_el = wiersz.query_selector(".smv__playerName")
                        if nazwisko_el:
                            strzelcy.append(nazwisko_el.inner_text().strip())

                mecz['scorers'] = ",".join(strzelcy)
                
                response = requests.post(URL_PHP, data=mecz, timeout=10)
                if response.status_code == 200:
                    logging.info(f"Sukces: {mecz['home']} - {mecz['away']}")
                else:
                    logging.warning(f"Błąd PHP (kod {response.status_code}): {mecz['home']}")
                
                time.sleep(2)
            except Exception as e:
                logging.error(f"Błąd przy meczu {mecz['home']}: {e}")

        browser.close()
        logging.info("Proces zakończony.")

if __name__ == "__main__":
    scraper()
