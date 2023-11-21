import os
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException as TS
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.common.by import By
import pickle as pk
import requests


def url_builder(root_url, page_number):
    url = f"{root_url}/page/{page_number}"
    return url


def fetch_links(driver, url):
    links = []

    def scraper_logic(url):
        print(f"Fetching job links from {url}")
        driver.get(url)
        x = 1  # Starting value of x
        skip_counter = 0

        while x < 24:
            try:
                # Construct the XPath for the div with the current x value
                xpath = f" //*[@id='main']/ul/li[{x}]/a"

                # /html/body/div/div/div/div/div/div[2]/main/ul/li[2]/a

                # try to get the element specified by the xpath, if it does not exist skip it
                try:
                    WebDriverWait(driver, 1).until(
                        conditions.presence_of_element_located((By.XPATH, xpath))
                    )
                except TS:
                    x += 1
                    skip_counter += 1
                    continue

                element = driver.find_element_by_xpath(xpath)
                try:
                    # Find and store the first link within the div, if it exists
                    links.append(element.get_attribute("href"))

                except NoSuchElementException:
                    pass

                x += 1  # Increment x for the next iteration

            except NoSuchElementException:
                # When there are no more divs with the current x value, exit the loop
                break

    driver.get(url)
    pagination = check_pagination(driver)

    if pagination > 0:
        print(f"Found {pagination} paginated pages, adding them to queue")
        sub_urls = [url]
        for page_number in range(2, pagination + 1):
            sub_urls.append(url_builder(url, page_number))

        for url in sub_urls:
            scraper_logic(url)

    return links


def check_pagination(driver):
    # returns number of pages if pagination exits or false if none

    try:
        xpath = '//*[@id="main"]/nav/ul'

        WebDriverWait(driver, 1).until(
            conditions.presence_of_element_located((By.XPATH, xpath))
        )
        pagination = driver.find_element(By.XPATH, xpath)

        pages = pagination.find_elements_by_tag_name("li")

        last_page = int(pages[-2].text)

        return last_page
    except TS:
        return False


def store_links(links):
    filename = "Outputs/codingkenya.pk"
    try:
        file = open(filename, "wb")
    except FileNotFoundError:
        print("Links folder not found, creating one.")
        os.mkdir("Outputs/")
        file = open(filename, "wb")

    pk.dump(links, file)
    file.close()

    print(
        f"Done. {len(links)} links from CodingJobs Kenya have been fetched and pickled🫙"
    )


def main():
    options = Options()
    options.add_argument("--headless")
    urls = ["https://codingkenya.com/job-category/"]
    links = []

    categories = [
        "artificial-intelligence",
        "automation",
        "backend-engineer",
        "big-data",
        "blockchain-developer",
        "cloud-solutions-architect",
        "data-engineer",
        "data-officer",
        "database-administrator",
        "coding",
        "cybersecurity",
        "devops-engineer",
        "digital-complience-and-audit",
        "digital-learning-specialist",
        "front-end-developer",
        "front-end-engineer",
        "fullstack-engineer",
        "full-stack-web-developer",
        "graphic-designer",
        "ict-officer",
        "helpdesk-support-analyst",
        "internet-of-things",
        "internship",
        "it-administrator",
        "it-consulting",
        "machine-learning",
        "software-developer",
        "software-engineer",
        "senior-software-engineer",
        "systems-administrator",
        "systems-developer",
        "ui-ux-designer",
        "web-developer",
    ]

    driver = webdriver.Chrome(options=options)

    # starts from page 2 because page 1 is already accounted for in the initial list

    tac = time.perf_counter()

    for category in categories:
        urls.append(urls[0] + category)

    for url in urls[1:]:
        # Check if page exists/returns a 404
        response = requests.get(url)
        if response.status_code == 404:
            print("Link does not exist. Stopping...")
            break
        else:
            links.append(fetch_links(driver, url))
            # print(fetch_links(driver, url))

    tic = time.perf_counter()

    # flattening the lists into one dimension
    links = [link for sublist in links for link in sublist]
    store_links(links)

    print(f"Time Taken:. {(tic - tac):.3f} seconds")

    # Closes driver agent
    driver.quit()


if __name__ == "__main__":
    main()
