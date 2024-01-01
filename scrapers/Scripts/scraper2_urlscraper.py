import os

from bs4 import BeautifulSoup
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import re


class Scraper:
    def __init__(self, thread, links, global_bar=None):
        self.thread = thread
        self.links = links
        self.global_bar = global_bar

        # making output directory if it doesn't exist
        directory = "Outputs/jobs"

        # TODO clearing existing files.

        os.makedirs(directory, exist_ok=True)

        filename = f"output{self.thread}.json"

        self.path = os.path.join(directory, filename)

        # Selenium instance setup
        options = Options()
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/109.0.0.0 Safari/537.36"
        )
        options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(options=options)

    @staticmethod
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

    def scraper(self, urls):
        jobs = {}
        skipped = 0

        # using regex to determine the site that is about to be scraped and to adjust the xpath to be used accordingly
        brightermonday = re.compile(r"brightermonday", re.IGNORECASE)
        codingkenya = re.compile(r"codingkenya", re.IGNORECASE)
        myjobmag = re.compile(r"myjobmag", re.IGNORECASE)

        for url in urls:
            try:
                if brightermonday.search(url):
                    xpath = {
                        "company": '//h2[@class="pb-1 text-sm font-normal"]',
                        "title": '//*[@id="tab1"]/div/article/div[2]/div[2]/h1',
                        "description": "//*[@id='tab1']/div/article/div[5]/div",
                        "location": '//*[@id="tab1"]/div/article/div[2]/div[2]/div[1]/*[1]',
                        "nature": '//*[@id="tab1"]/div/article/div[2]/div[2]/div[1]/*[2]',
                        "salary": '//*[@id="tab1"]/div/article/div[2]/div[2]/div[2]/span[1]/span',
                        "posted": '//*[@id="tab1"]/div/article/div[3]/div[2]',
                    }
                elif codingkenya.search(url):
                    xpath = {
                        "title": "/html/body/div/div/header[2]/div/div/div[1]/h1",
                        "description": "/html/body/div/div/div/div/div/div[2]/main/div/div/div[1]/div[2]/article/div/div[1]",
                        "location": "/html/body/div/div/header[2]/div/div/div[1]/div/ul/li[2]/a",
                        "nature": "/html/body/div/div/header[2]/div/div/div[1]/div/ul/li[1]",
                    }
                elif myjobmag.search(url):
                    xpath = {
                        "title": "/html/body/section/div/div/div[1]/ul/li[3]/h2[1]/span",
                        "description": "//*[@id='printable']/div[2]",
                        "location": '//*[@id="printable"]/ul/li[4]/span[2]/a',
                        "nature": '//*[@id="printable"]/ul/li[1]/span[2]/a',
                        "salary": '//*[@id="tab1"]/div/article/div[2]/div[2]/div[2]/span[1]/span',
                        "posted": '//*[@id="posted-date"]',
                    }

                self.driver.get(url)
                try:
                    WebDriverWait(self.driver, 20).until(
                        conditions.presence_of_element_located(
                            (By.XPATH, xpath["description"])
                        ),
                    )

                    #  get job details and clean innerHTML from posted and description
                    title = self.driver.find_element_by_xpath(xpath["title"])
                    location = self.driver.find_element_by_xpath(xpath["location"])
                    nature = self.driver.find_element_by_xpath(xpath["nature"])
                    # salary = self.driver.find_element_by_xpath(xpath["salary"])
                    description = self.parser(
                        dirty=self.driver.find_element_by_xpath(
                            xpath["description"]
                        ).get_attribute("innerHTML")
                    )

                    # updating the jobs dict with key value pairs of {url:{job details}}

                    jobs.update(
                        {
                            url: {
                                "title": title.text,
                                "location": location.text,
                                "nature": nature.text,
                                # "salary": (
                                #     salary.text
                                #     if len(salary.text) > 6
                                #     else "Unspecified"
                                # ),
                                "description": description,
                            }
                        }
                    )
                    # self.local_progress.update(1)
                    self.global_bar.update(1)

                except TimeoutException:
                    skipped += 1

            except NoSuchElementException:
                print("Hii stuff haiko buda")
                return jobs, skipped
            except TimeoutException:
                return jobs, skipped

        return jobs, skipped

    def store(self, jobs):
        file = json.JSONEncoder().encode(jobs)
        f = open(self.path, "w")

        f.write(file)
        f.close()

        print(f"{len(jobs)} listing(s) have been serialized and stored.")

    def run(self):
        jobs, skipped = self.scraper(self.links)

        if skipped > 0:
            print(f"Completed {len(jobs)} jobs, {skipped} skipped due to timeout)")

        self.store(jobs)

        if self.global_bar is not None:
            self.global_bar.update(1)
