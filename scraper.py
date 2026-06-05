from playwright.sync_api import sync_playwright
import requests

URL_PHP = "https://worldbetapp.cba.pl/auto_fetch_results.php"


def scraper():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.flashscore.pl/pilka-nozna/swiat/mecze-towarzyskie/")
        page.wait_for_selector(".sportName")

        mecze = page.query_selector_all("[class*='event__match']")
        print(f"Przetwarzam {len(mecze)} elementów...")

        for mecz in mecze:
            # Pobieramy czysty tekst i dzielimy go na linie
            linie = mecz.inner_text().split('\n')

            # Szukamy tylko meczów zakończonych (status 'Koniec')
            # i sprawdzamy czy mamy wystarczająco dużo linii (min 5: status, dom, wyjazd, gol1, gol2)
            if len(linie) >= 5 and linie[0] == "Koniec":
                data = {
                    'home': linie[1],
                    'away': linie[2],
                    'h_score': linie[3],
                    'a_score': linie[4]
                }

                print(f"WYSYŁAM: {data['home']} {data['h_score']}:{data['a_score']} {data['away']}")

                try:
                    requests.post(URL_PHP, data=data, timeout=5)
                except Exception as e:
                    print(f"Błąd wysyłki: {e}")

        browser.close()


if __name__ == "__main__":
    scraper()