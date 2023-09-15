from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException as TS
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.common.by import By
import pickle as pk


def url_builder(page):
    url = f"https://www.myjobmag.co.ke/jobs-by-field/information-technology/{page}"
    return url


def fetch_links(driver, url):
    driver.get(url)

    # wait for the page to load
    WebDriverWait(driver, 10)

    links = []
    x = 1  # Starting value of x
    skip_counter = 0

    while x < 24:
        try:
            # Construct the XPath for the div with the current x value
            xpath = f"//*[@id='cat-left-sec']/ul/li[{x}]/ul/li[2]/ul/li[1]/h2/a"

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

    # Removing any duplicates and misleading links
    # links = [link for link in links if "listings" in link]
    # links = list(set(links))

    return links


def store_links(links):
    file = open('links/myjobmag_links', 'wb')
    pk.dump(links, file)
    file.close()

    def main():
        options = Options()
        options.add_argument("--headless")
        urls = ["https://www.myjobmag.co.ke/jobs-by-field/information-technology"]
        links = []

        driver = webdriver.Chrome(options=options)

        # Adding the paginated pages to the root url
        # done up to page 5 to limit the results to recent information only
        # starts from page 2 because page 1 is already accounted for in the initial list
        for x in range(2, 10):
            urls.append(url_builder(x))

        for x in urls:
            print(f"Fetching job links from {x}")
            links.append(fetch_links(driver, x))

        # flattening the lists into one dimension
        links = [link for sublist in links for link in sublist]
        store_links(links)

        print(f"Done. {len(links)} links have been fetched and pickled🫙")
        # Closes driver agent
        driver.__exit__()

    if __name__ == "__main__":
        main()