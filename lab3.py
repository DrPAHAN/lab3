import csv
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


BASE_URL = "https://quotes.toscrape.com"
MAX_PAGES = 3
CSV_FILE = "quotes_data.csv"

def setup_driver():
    opts = Options()
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    return webdriver.Chrome(options=opts)

def parse_page(driver, page_num):
    wait = WebDriverWait(driver, 10)
    try:
        quotes = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "quote")))
        print(f"Страница {page_num}: найдено цитат → {len(quotes)}")
    except Exception as e:
        print(f"Страница {page_num}: элементы не загрузились за 10 сек. {e}")
        return []

    results = []
    for q in quotes:
        try:
            text = q.find_element(By.CLASS_NAME, "text").text
            author = q.find_element(By.CLASS_NAME, "author").text
            tags = ", ".join([t.text for t in q.find_elements(By.CLASS_NAME, "tag")])
            source_url = q.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            
            results.append({
                "page": page_num,
                "quote_text": text,
                "author": author,
                "tags": tags,
                "source_url": source_url
            })
        except Exception as e:
            print(f"Ошибка при разборе элемента: {e}")
    return results

def handle_pagination(driver):
    data = []
    driver.get(BASE_URL)
    
    for page in range(1, MAX_PAGES + 1):
        print(f"\nПарсинг страницы {page}...")
        data.extend(parse_page(driver, page))
        
        try:
            next_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li.next a"))
            )
            next_btn.click()
            time.sleep(2)
        except Exception:
            print(f"Кнопка 'Next' не найдена или не кликабельна. Пагинация завершена.")
            break
            
    return data

def save_to_csv(data, filename):
    if not data:
        print("\nОШИБКА: Нет данных для сохранения!")
        return
        
    fieldnames = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        
    print(f"\nФайл успешно сохранён: {os.path.abspath(filename)}")
    print(f"Всего записей: {len(data)}")

if __name__ == "__main__":
    print("Запуск парсера...")
    driver = setup_driver()
    try:
        all_data = handle_pagination(driver)
        save_to_csv(all_data, CSV_FILE)
    finally:
        driver.quit()
        print("Браузер закрыт.")