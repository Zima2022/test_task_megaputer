import csv
import re

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait as Wait, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def driver():
    options_chrome = webdriver.ChromeOptions()
    options_chrome.add_argument('--headless')
    driver_service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=driver_service, options=options_chrome)


def fix_first_row(some_string: str) -> str:
    """
    Исправляет первую строчку в списке сертификатов.
    Возвращает строку с названием сертификата и датой его получения.
    """
    return some_string.split(') ')[-1]


def find_element(browser, locator):
    return WebDriverWait(browser, 1).until(EC.visibility_of_element_located(locator))


def prepare_for_write_to_file(person, certificates=None) -> list[list[str, str, str]]:
    result = []
    certificates = certificates.copy() if certificates else None
    pattern = r'([А-я\s-]+[а-я]) (\d\d\.\d\d\.\d{4})'
    for certificate in certificates:
        name, date = re.findall(pattern, certificate)[0]
        result.append([person, name, date])
    return result


def main() -> None:
    data = []
    browser = driver()
    browser.get('https://www.megaputer.ru/produkti/sertifikat/')

    with open('persons.csv', encoding='utf-8') as file:
        for person in csv.reader(file):
            input_field = Wait(browser, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#certificates-text'))
            )
            input_field.send_keys(*person)
            input_field.send_keys(Keys.RETURN)
            try:
                element = find_element(browser, (By.TAG_NAME, 'table'))
                certificates = element.text.split('\n')[2:]
                certificates[0] = fix_first_row(certificates[0])
                data.extend(prepare_for_write_to_file(*person, certificates))
            except TimeoutException:
                data.extend([[*person, '', '']])
            browser.get('https://www.megaputer.ru/produkti/sertifikat/')

    with open('results.csv', mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)


if __name__ == '__main__':
    main()
