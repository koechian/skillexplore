# skillexplore

Aims to scrape IT job listings from Kenyan online Job Boards for analysis and data mining to extract a factual list of skills and requirements for certain fields in the tech space. 

I found that some companies asked for an overwhelming amount of technologies, or sometimes have poorly written job descriptions/requirements lists that wore posted by HR representatives who have no knowledge of what skills are required for certain roles.
This would have a fresh graduate (and even experienced job-seekers) misunderstand the role and what is required, leading to them flunking the interview.

So I decided to scrape, data mine and compile my findings regarding job skills and realtime market demand into a single interface to help other students decide what to invest their time into learning
in campus before venturing into the job market to give them the best opportunity to succeed in getting a Tech Job in the currently competitive job market.

## 1. Scraping Module (Data Collection)

- Job listings were scraped using a headless selenium instance. 
- Only listings that were in the IT space were crawled from:
  1. [Brighter Monday](https://www.brightermonday.co.ke)
  2. [My Job Mag](https://www.myjobmag.co.ke)
  3. [LinkedIn](https://www.linkedin.com/jobs) [to be added]

- The job listings were scraped from the general listings page and stored in a data object as urls.
- For example, in the listing below, the link in 'Data Science Interns at Nakala Analytics Ltd' would be scraped and stored in a Data Object. 
- ![example url.png](assets%2Fexample%20url.png)
- These listings were then imported by an url crawler script that would then visit each and every link and scrape the Job Listing for the following fields:
  1. Company
  2. Job Title / Role
  3. Job Description
  4. Location
  5. Nature --> [internship, fulltime, remote, part-time]
  6. Salary (if available)
  7. Date Posted

- The data was then pre-processed by:
  1. Removing newline characters "/n"
  2. Removing tab spaces and large spaces. 
  3. Removing special HTML characters
![Clean Up Steps](assets%2Fcleanup.png)
- Further cleaning steps such as lemmatisation, data splitting and transofmation into a pandas dataframe will be done in the NLP module
### Pinch points
- The speed of scraping the data needs to be improved. This can (and will be done) by making several instances of selenium webcrawlers run on different urls in parallel. The 'urls' list can be split into many fragments and separate instances called to work on each segment. 
- LinkedIn needs login credentials to allow one to view job listings.

## 2. NLP Module

- An NLP model is used to differentiate qualification/requirements sentences from general description sentences and extract key skills that are required from each listing.
- This module should be able to take in the data from the Scraping Module and perform the following tasks:
  1. Clean it further if need be.
  2. Take in the job listing and return a list of skills associated with the job listing.

### The Dataset.

The dataset is collected from Singaporean government website, mycareersfuture.sg consisting of over 20, 000 richly-structured job posts. The detailed statistics of the dataset are shown below:

Mycareersfuture.sg Dataset |  Stats
--- | ---
Number of job posts | 20,298
Number of distinct skills | 2,548
Number of skills with 20 or more mentions | 1,209
Average skill tags per job post | 19.98
Average token count per job post | 162.27
Maximum token count in a job post | 1,127


This dataset includes the following fields:

1. company_name
2. job_title
3. employment_type
4. seniority
5. job_category
6. location
7. salary
8. min_experience
9. skills_required
10. requirements_and_role
11. job_requirements
12. company_info
13. posting_date
14. expiry_date
15. no_of_applications
16. job_id

- For my use and also to make the large dataset more managable, I dropped several fields that I considered not needed in trainning. These included:
  1. company_name
  2. location (all are either Singapore or remote)
  3. company_info
  4. posting_date
  5. expiry_date
  6. no_of_applicants
  7. job_id
  8. seniority