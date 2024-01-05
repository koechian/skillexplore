import os
import pickle as pk
from tqdm import tqdm
import time


from scripts.scraper2_urlscraper import Scraper
import scripts.scraper1_brightermonday as bm
import scripts.scraper1_myjobmag as mjm
import scripts.scraper1_codingkenya as cdk

from scripts.util import Utilities


def fetch_links():
    files = os.listdir("scrapers/Outputs/links/")
    urls = []
    for file in files:
        print(f"Fetched {file}")
        _ = open(("scrapers/Outputs/links/" + file), "rb")
        urls.append(pk.load(_))

    urls = [url for sublist in urls for url in sublist]

    # randomly shuffling the Urls to prevent hitting rate limits by pinging one website constantly

    # urls = random.shuffle(urls)

    print(f"{len(urls)} urls have been unpacked from {len(files)} found files")
    return urls


def preScrapers():
    # Run the pre-scrapers
    bm.main()
    mjm.main()
    cdk.main()


def split_links(links, cpus):
    size = round((len(links) / cpus))

    final = [
        links[i * size : (i + 1) * size] for i in range((len(links) + size - 1) // size)
    ]
    return final


def linker(urls, index, global_bar):
    instance = Scraper(links=urls, thread=index, global_bar=global_bar)
    instance.run()


def main():
    if Utilities.internet_check():
        # run the prescrapers to get URLS

        # preScrapers()

        raw_links = fetch_links()

        global_bar = tqdm(total=len(raw_links), desc="Total Progress: ")

        tac = time.perf_counter()
        linker(raw_links, 1, global_bar)

        global_bar.close()

        tic = time.perf_counter()

        print(f"Time taken is: {tic - tac} Seconds")
    else:
        return


if __name__ == "__main__":
    main()
