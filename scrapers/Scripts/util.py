# Utility functions that are called by multiple scripts

import requests


class Utilities:
    @staticmethod
    def internet_check():
        availability = False
        try:
            requests.get("https://www.google.com")
            availability = True
        except requests.exceptions.ConnectionError:
            print("Internet check failed, check if you are connected.")
        except requests.exceptions.Timeout:
            print("Internet check failed, check if you are connected.")

        return availability
