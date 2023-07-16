# Installing Selenium WebDriver with Python and PyCharm
# https://alexsl.medium.com/installing-selenium-webdriver-with-python-and-pycharm-from-scratch-on-windows-e4c713043882
# On the right corner of PyCharm to choose run current file
# On te button of PyCharm window clik on Packages, search and download libraries selenium and bs4
# Make sure to close the linkedin-jobs.csv file before running this program
# please remove the words inside quotation of email and password if share the code to others!
import json
import os
import time
import random
from selenium import webdriver
import csv
from bs4 import BeautifulSoup
import datetime

current_date = datetime.datetime.now()

# load selenium driver
driver = webdriver.Chrome()
driver.get('https://linkedin.com/')
time.sleep(random.randint(1, 4))


def find_page_num(html_soup):
    try:
        page_string = html_soup.find('div', class_="artdeco-pagination__page-state").text.strip()
        # print("page_string", page_string)
        page_number = int(page_string.split(" ")[-1])
        # print("page_number", page_number)
        return page_number
    except:
        page_number = 1
        print("No page number found or less than one page job found")
        return page_number


def check_exist_id(job_id, json_job_file):  # return true if the job id is in the json file
    try:
        with open(json_job_file, 'r') as jsonfile:
            json_data = json.loads(jsonfile.read())
            if job_id in json_data:
                return True
            else:
                return False
    except:
        return False


def write_json(job_id, job_detail, json_job_file):
    try:
        # read file
        open_file = open(json_job_file, 'r')
        load_dict = json.load(open_file)
        open_file.close()
        # print(type(load_dict))
        # add job detail
        load_dict[job_id] = job_detail
    except:  # if the file is empty which is not able to load
        load_dict = {job_id: job_detail}

    try:
        # dump back into a json file
        dump_file = open(json_job_file, 'w')
        json.dump(load_dict, dump_file, indent=3)
        dump_file.close()
    except:
        print(f"Error on write the {job_id} into JSON file")


def get_job_ids(html_soup, job_ids_list):  # get the key id of each page
    li_list = html_soup.find_all('li')
    for each_li in li_list:
        job_id = each_li.get('data-occludable-job-id')
        if job_id is not None and job_id not in job_ids_list:
            job_ids_list.append(job_id)


def find_job_post_date(job_info_time):  # convert the list day to date
    if 'minute' in job_info_time or 'hour' in job_info_time:
        return f'{current_date.month}/{current_date.day}/{current_date.year}'
    elif "day" in job_info_time:
        num = ""
        for c in job_info_time:
            if c.isdigit():
                num = num + c
        job_date = datetime.datetime.now() - datetime.timedelta(days=int(num))
        return f'{job_date.month}/{job_date.day}/{job_date.year}'
    elif "week" in job_info_time:
        num = ""
        for c in job_info_time:
            if c.isdigit():
                num = num + c
        job_date = datetime.datetime.now() - datetime.timedelta(days=int(num) * 7)
        return f'{job_date.month}/{job_date.day}/{job_date.year}'
    elif "month" in job_info_time:
        num = ""
        for c in job_info_time:
            if c.isdigit():
                num = num + c
        job_date = datetime.datetime.now() - datetime.timedelta(days=int(num) * 30)
        return f'{job_date.month}/{job_date.day}/{job_date.year}'
    else:
        print(job_info_time)
        return "No info"


def view_jobs(job_ids, job_json_file):
    new_row_count = 0
    cout_job_id = 0
    for job_id in job_ids:
        cout_job_id += 1
        if not check_exist_id(job_id, job_json_file):
            job_link = f"https://www.linkedin.com/jobs/view/{job_id}/"
            driver.get(job_link)
            time.sleep(random.randint(1, 4))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            try:
                try:
                    job_title = soup.find('h1', class_='jobs-unified-top-card__job-title').text.strip()
                except:
                    job_title = "no info"

                try:
                    job_company = soup.find('a', class_="ember-view t-black t-normal").text.strip()
                except:
                    job_company = "no info"

                try:
                    job_location = soup.find('span', class_='jobs-unified-top-card__bullet').text.strip()
                except:
                    job_location = "no info"

                try:
                    job_onsite = soup.find('span', class_='jobs-unified-top-card__workplace-type').text.strip()
                except:  # so website don't have on site code in the HTML which mean it is in person
                    job_onsite = ''

                try:
                    job_time = soup.find('span', class_='jobs-unified-top-card__posted-date').text.strip()
                    list_date = find_job_post_date(job_time)
                except:
                    list_date = 'no info'

            except:
                job_title = "no info"
                job_company = "no info"
                job_location = "no info"
                job_onsite = ''
                list_date = 'no info'
                print(f"Not able to find job details on {job_link}")

            try:
                writer.writerow([job_company, job_title, list_date, job_time, job_link, job_location, job_onsite])
            except:
                print(f"Error of writing row on the CSV file of {job_id}")
            try:
                write_json(job_id,
                           {"job_company": job_company, "job_title": job_title, "list_date": list_date,
                            "job_time": job_time,
                            "job_link": job_link, "job_location": job_location, "job_onsite": job_onsite},
                           job_json_file)
            except:
                print(f"There is error on reading and writing the json record of {job_id}")

            new_row_count += 1  # count how many rows will the CVS file will update
            print(f"{cout_job_id} out of {len(job_ids)} jobs:\n",
                  [job_company, job_title, list_date, job_time, job_link, job_location, job_onsite])
        else:
            print(f"{cout_job_id} out of {len(job_ids)} jobs:\nJob {job_id} has existed in the JSON file")
    print(f'{new_row_count} rows of jobs updated on the CSV file')


def loop_through_pages(url, page_num, job_ids_list):  # loop through each page and get the id in each page
    time.sleep(random.randint(1, 4))
    if page_num <= 1:
        html_soup = BeautifulSoup(driver.page_source, 'html.parser')
        get_job_ids(html_soup, job_ids_list)
        print(job_ids_list)
    else:
        for i in range(1, page_num):
            start_num = i * 25
            new_url = url + f"&start={start_num}"
            print(new_url)
            driver.get(new_url)
            time.sleep(random.randint(1, 4))
            html_soup = BeautifulSoup(driver.page_source, 'html.parser')
            try:
                get_job_ids(html_soup, job_ids_list)
            except:
                print(f"cannot find job ids in this page {new_url}")


input(
    "Please login your linkedin account on the pop up chrome browser, \n please type Y and Enter to continue after you "
    "login (make sure to do the security check if necessary) ")
job_name = input('Enter Job or Skill: ').strip()
job_place = input('Enter the Location: ').strip()
# # job_name = "software engineer"
# # job_place = "New York"
job_json_file = 'linkedin_jobs.json'
job_csv_file = 'linkedin_jobs.csv'
if not os.path.isfile(job_json_file):
    with open(job_json_file, 'w') as fp:
        pass

# read CSV file
read_csv_file = open(job_csv_file, 'a', newline='')
writer = csv.writer(read_csv_file)
writer.writerow(['Company', 'Title', 'List Date', 'Job Time', 'Job Link', 'Location', 'Comments/Notes'])

url = f"https://www.linkedin.com/jobs/search/?keywords={job_name}&location={job_place}&refresh=true"
driver.get(url)
time.sleep(random.randint(1, 4))
html_soup = BeautifulSoup(driver.page_source, 'html.parser')
job_ids_list = []  # scrape the job id for each page
page_num = find_page_num(html_soup)
print(f"Number of pages found in this job searching: {page_num}")

try:
    # get all the page number, then go on each page,
    # get all the job ids in that page, append job id the job id list
    loop_through_pages(url, page_num, job_ids_list)
    print("job_ids", job_ids_list)
    # with open('job_ids_list.txt', 'w') as tfile:
    #     # put the current job_ids_list into a text file, but every time you run the programing will cover the
    #     # previous program runs
    #     tfile.write('\n'.join(job_ids_list))
except:
    print("Error on check on job pages")
    time.sleep(60)

try:
    view_jobs(job_ids_list, job_json_file)
    print("The program finished running")
    driver.close()
except:
    print(
        "Error on viewing a job id and please check on the next job id in the list")
    input("Enter E to end the chrome browser:")
    time.sleep(10)
read_csv_file.close()
