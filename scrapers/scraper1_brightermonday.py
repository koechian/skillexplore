from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.common.by import By
import pickle as pk


def url_builder(page):
    url = f"https://www.brightermonday.co.ke/jobs/software-data?page={page}"
    return url


def fetch_links(driver, url):
    driver.get(url)

    # wait for the page to load
    WebDriverWait(driver, 5)

    links = []
    roles = []
    x = 3  # Starting value of x

    while x < 24:
        try:
            # Construct the XPath for the div with the current x value
            xpath = f"/html/body/main/section/div[2]/div[2]/div[1]/div[{x}]"
            WebDriverWait(driver, 1).until(
                conditions.presence_of_element_located((By.XPATH, xpath))
            )
            element = driver.find_element_by_xpath(xpath)

            try:
                # Find and store the first link within the div, if it exists
                link = element.find_element_by_tag_name("a")
                links.append(link.get_attribute("href"))

            except NoSuchElementException:
                pass

            x += 1  # Increment x for the next iteration

        except NoSuchElementException:
            # When there are no more divs with the current x value, exit the loop
            break

    # Removing any duplicates and misleading links
    links = [link for link in links if "listings" in link]
    links = list(set(links))

    return links


def store_links(links):
    file = open("links/brightermonday_links", "wb")
    pk.dump(links, file)
    file.close()


def main():
    options = Options()
    options.add_argument("--headless")
    urls = ["https://www.brightermonday.co.ke/jobs/software-data"]
    links = []

    driver = webdriver.Chrome(options=options)

    # Adding the paginated pages to the root url
    # done up to page 5 to limit the results to recent information only
    # starts from page 2 because page 1 is already accounted for in the initial list
    for x in range(2, 11):
        urls.append(url_builder(x))

    for url in urls:
        print(f"Fetching job links from {url}")
        links.append(fetch_links(driver, url))

    # flattening the lists into one dimension
    links = [link for sublist in links for link in sublist]
    store_links(links)

    print(f"Done. {len(links)} links have been fetched and pickled🫙")
    # Closes driver agent
    driver.__exit__()


if __name__ == "__main__":
    main()
