import os
import pickle as pk
from tqdm import tqdm
from scrapers.Scripts.scraper2_urlscraper import Scraper
import time
from multiprocessing import cpu_count, Process

from scrapers.Scripts.util import Utilities


def fetch_links():
    files = os.listdir("links/")
    urls = []
    for file in files:
        _ = open(("links/" + file), "rb")
        urls.append(pk.load(_))

    urls = [url for sublist in urls for url in sublist]

    print(f"{len(urls)} urls have been unpacked.")
    return urls


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
        # Generate a number of processes equal to the number of CPU's in the system minus 2.
        # cpus = cpu_count() - 2
        raw_links = fetch_links()
        #
        # links = split_links(raw_links, cpus)
        # instance = []

        global_bar = tqdm(total=len(raw_links), desc="Total Progress: ")

        tac = time.perf_counter()

        # for index, x in enumerate(raw_links):
        #     inst = Process(target=linker, args=(x, index, global_bar))
        #     instance.append(inst)
        #     inst.start()
        #
        # for i in instance:
        #     i.join()

        linker(raw_links, 1, global_bar)

        global_bar.close()

        tic = time.perf_counter()

        print(f"Time taken for MultiProcessing is: {tic - tac} Seconds")
    else:
        return


if __name__ == "__main__":
    main()

# Without multiprocessing time taken for 444 links with 10 mbps net was 73 mins
# with 106 jobs completed and 338 skipped due to timeout