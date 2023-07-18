# In line 17, change the job title you are looking for
# be sure to look at the right path in line 11 when you are runing

import re
import csv
import requests
from bs4 import BeautifulSoup
from time import sleep
from random import randint
import os.path

save_path = 'C:/Users/username/Desktop/jobs/' # put the path that save the files
name_of_file = "Error Links" 
csv_file_name = "Job Posting"
error_file = os.path.join(save_path, name_of_file + ".txt") 
csv_file = os.path.join(save_path, csv_file_name + ".csv") # Please make sure to close the csv file before runing the program

jk_pattern = re.compile(r"jk:\'([a-zA-Z0-9]+)'")
params = { "q": "Software Enginer intern", "l": "new york", "start": 0 }  ### INPUT the tittle of job title you are looking
url = "https://www.indeed.com/jobs"
job_keys = set()

for x in range(10):
    response = requests.get(url, params=params)
    if not response.status_code == 200:
        break
    else:
        keys = jk_pattern.findall(response.text)
        if len(keys) > 0:
            for key in keys:
                job_keys.add(key)
    
    params['start'] += 20
    sleep(randint(0, 3))

template = "https://www.indeed.com/viewjob?jk={}"

job_list = []
fields = ['Company', 'Job Title', 'Job acitivity', 'Link', 'Description']

print(f"{len(job_keys)} interns found")
for jk in job_keys:
    job_url = template.format(jk) 
    response = requests.get(job_url)
    soup = BeautifulSoup(response.text, 'html.parser') 

    print(job_url)

    company = re.compile('.*jobsearch-CompanyReview--heading.*')
    title = re.compile('.*title.*') 
    activity = re.compile('.*jobsearch-HiringInsights-entry--text.*')
    row_dict = dict()
    try:
        row_dict['Company'] = soup.find('div', {'class': company}).text
        row_dict['Job Title'] = soup.find('h1', {'class': title}).text
        row_dict['Job acitivity'] = soup.find('span', {'class': activity}).text
        while 'Posted' not in soup.find('span', {'class': activity}).text:
            row_dict['Job acitivity'] = soup.findNext('span', {'class': activity}).text
        row_dict['Link'] = job_url
        row_dict['Description'] = "" 
    except:
        try:
            row_dict['Company'] = soup.find('div', {'class': re.compile('.*InlineCompanyRating.*')}).text
            row_dict['Job Title'] = soup.find('h1', {'class': title}).text
            row_dict['Job acitivity'] = soup.find('span', {'class': activity}).text
            while 'Posted' not in soup.find('span', {'class': activity}).text:
                row_dict['Job acitivity'] = soup.findNext('span', {'class': activity}).text
            row_dict['Link'] = job_url
            row_dict['Description'] = "" 
        except:
            row_dict['Link'] = job_url
            print(f"Error URL: {job_url}")

    job_list.append(row_dict)


with open(csv_file, 'a', newline='') as csvfile: 
    writer = csv.DictWriter(csvfile, fieldnames = fields) 
    writer.writeheader() 
    writer.writerows(job_list)
