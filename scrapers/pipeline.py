# This script is charged with cleaning the scraped data, modelling the format to something more stuructured and uploading to the database

import os
import json
import pandas as pd
import contractions
from regex import P
import requests
from seaborn import load_dataset


class Pipeline:
    def __init__(self, path):
        self.path = path

    @staticmethod
    def upload(jsonData):
        api = "http://127.0.0.1:5000/scraped"

        response = requests.post(api, json=jsonData)

        if response.status_code == 200:
            print("Data sent to API")
        else:
            print(str(response.status_code) + ":" + str(response.text))

    def loadData(self):
        # Reads data from json files and concatenates them into one df
        # Loading in Data and cleaning

        path = self.path
        temp = []

        for index, file in enumerate(os.listdir(path)):
            print(f"Loaded batch {index + 1}")
            try:
                with open(f"{path}/{file}") as jsonfile:
                    data = pd.DataFrame.from_dict(json.load(jsonfile), orient="index")
                    temp.append(data)
            except UnicodeDecodeError:
                print("Skipping due to unicode error")

        # with open(f"{path}/batch1.json") as jsonFile:
        #     data = pd.DataFrame.from_dict(json.load(jsonFile), orient="index")
        #     temp.append(data)

        # Concatenating output into one DataFrame
        df = pd.concat(temp, ignore_index=True)

        return df

    @staticmethod
    def cleaner(df):
        # Dropping listings without description
        df = df[df["description"] != "None"]

        # Renaming remote locations to only remote
        df.loc[
            df["location"].str.contains("remote", case=False, regex=False), "location"
        ] = "Remote"

        # Remove occurrences of the word "County"
        df["location"] = df["location"].str.replace(r" County", "", regex=True)

        # Splitting the 'location' column into 'city' and 'county' columns
        df[["city", "county"]] = df["location"].str.split(",| ", expand=True, n=1)

        # Drop the now redundant Location and Country Cols since we know all listings are from Kenya
        df = df.drop("location", axis=1)
        df = df.drop("county", axis=1)

        # rename the City col to location
        df.rename(columns={"city": "location"}, inplace=True)

        # removing contractions
        # df["description"] = df["description"].str.replace(
        #     r"CLICK HERE\b.*", "", regex=True, case=False
        # )

        df["description"] = df["description"].apply(
            lambda x: [contractions.fix(word) for word in x.split()]
        )

        # cocatenating items back into a single string
        df["description"] = [" ".join(map(str, l)) for l in df["description"]]

        return df

    @staticmethod
    def backToJSON(df):
        # Converts the batch file back to JSON encoded format
        return df.to_json(orient="index")

    @staticmethod
    def testJson(jsonData):
        # Write the json back to a file to see if format is correct
        with open("tester.json", "w") as file:
            file.write(jsonData)
            file.close()

    def run(self):
        data = self.loadData()
        cleaned = self.cleaner(data)
        cleanedJson = self.backToJSON(cleaned)
        # self.testJson(cleanedJson)

        self.upload(cleanedJson)


line = Pipeline("scrapers/Outputs/jobs")
line.run()
