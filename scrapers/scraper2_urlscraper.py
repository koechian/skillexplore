import pickle as pk
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


def fetch_links():
    files = os.listdir("links/")
    urls = []
    for file in files:
        _ = open(("links/" + file), "rb")
        urls.append(pk.load(_))

    urls = [url for sublist in urls for url in sublist]

    print(f"{len(urls)} urls have been unpacked.")
    return urls


def parser(dirty):
    # removing HTML tags
    raw = BeautifulSoup(dirty, "html.parser").get_text()

    text = (
        raw.replace("\n", " ")
        .replace("\xa0", " ")
        .replace("\u2019", "'")
        .replace("\u2013", "-")
        .replace("\u2022", "")
        .replace("\u201c", "")
        .replace("\u201d", '"')
        .replace("\u2014", "—")
    )

    # removing tab spaces and large spaces
    cleaned = " ".join(text.split())

    return cleaned


def scraper(driver, urls):
    jobs = {}
    skipped = 0

    for url in tqdm(urls, desc="Fetching"):
        try:
            xpath = {
                "company": '//h2[@class="pb-1 text-sm font-normal"]',
                "title": '//*[@id="tab1"]/div/article/div[2]/div[2]/h1',
                "description": "//*[@id='tab1']/div/article/div[5]/div",
                "location": '//*[@id="tab1"]/div/article/div[2]/div[2]/div[1]/*[1]',
                "nature": '//*[@id="tab1"]/div/article/div[2]/div[2]/div[1]/*[2]',
                "salary": '//*[@id="tab1"]/div/article/div[2]/div[2]/div[2]/span[1]/span',
                "posted": '//*[@id="tab1"]/div/article/div[3]/div[2]',
            }

            driver.get(url)
            try:
                WebDriverWait(driver, 10).until(
                    conditions.presence_of_element_located(
                        (By.XPATH, xpath["description"])
                    ),
                )

                #  get job details and clean innerHTML from posted and description
                company = driver.find_element_by_xpath(xpath["company"])
                title = driver.find_element_by_xpath(xpath["title"])
                location = driver.find_element_by_xpath(xpath["location"])
                nature = driver.find_element_by_xpath(xpath["nature"])
                salary = driver.find_element_by_xpath(xpath["salary"])

                # cleaning the output
                posted = parser(
                    driver.find_element_by_xpath(xpath["posted"]).get_attribute(
                        "innerHTML"
                    )
                )
                description = parser(
                    driver.find_element_by_xpath(xpath["description"]).get_attribute(
                        "innerHTML"
                    )
                )

                # updating the jobs dict with key value pairs of {url:{job details}}

                jobs.update(
                    {
                        url: {
                            "company": company.text,
                            "title": title.text,
                            "location": location.text,
                            "nature": nature.text,
                            "salary": (
                                salary.text if len(salary.text) > 6 else "Unspecified"
                            ),
                            "description": description,
                            "posted": posted,
                        }
                    }
                )

            except TimeoutException:
                skipped += 1

        except NoSuchElementException:
            print("Hii stuff haiko buda")
            return jobs, skipped

    return jobs, skipped


def store(jobs):
    file = json.JSONEncoder().encode(jobs)
    f = open("dumps.json", "w")

    f.write(file)
    f.close()

    print(f"{len(jobs)} listing(s) have been serialized and stored.")


def main():
    options = Options()
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/109.0.0.0 Safari/537.36"
    )
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)

    # call the functions
    urls = fetch_links()
    jobs, skipped = scraper(driver, urls)
    if skipped > 0:
        print(f"Completed {len(jobs)} jobs, {skipped} skipped due to timeout)")

    store(jobs)


if __name__ == "__main__":
    main()
