# !pip install schedule
# !pip install gspread
# !pip install oauth2client
# !pip install pytz

from bs4 import BeautifulSoup
import requests
import time
import json
import re
from urllib.parse import quote
import csv
import schedule
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pytz
from pytz import timezone

timezone_kolkata = pytz.timezone('Asia/Kolkata')

# skillsr = ['']
# skillsgth = []

# timezone_kolkata = pytz.timezone('Asia/Kolkata')

def find_jobs(soup,local_json_data=0):
    job_list = []
    jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')
    jobid_dict={}
    try:
      for id in local_json_data:
          id_data=id['Made Up JOB ID']
          jobid_dict[id_data]='True'
      print(jobid_dict)
    except TypeError:
      pass
    for job in jobs:
        idcounter=0
        title = job.a.text
        comp = job.find('h3', class_='joblist-comp-name').text
        job_location=job.find('i',class_="material-icons").find_next('span').text.strip()
        exp_req=job.find('li').text.replace('card_travel','')
        jobid_madeup = f"{title.strip().replace(' ','').lower()}{comp.strip().replace(' ','').lower()}{job_location.strip().replace(' ','').lower()}{exp_req.strip().replace(' ','').lower()}"
        # print(jobId)
        try:
          if jobid_dict[jobid_madeup]=='True':
            idcounter+=1
        except KeyError:
          pass
        if(idcounter==0):
          try:
            pdate = job.find('span', class_='sim-posted').span.text.strip()
            date=datetime.now().date()
            if 'today' in pdate.lower():
              pdate=date
              pdate=pdate.strftime('%d/%m/%Y')
              # print(f"Updated pdate after condition 1: {pdate}")
            elif '1' in pdate.lower():
              pdate=date- timedelta(days=1)
              pdate=pdate.strftime('%d/%m/%Y')
              # print(f"Updated pdate after condition 2: {pdate}")
            elif '2' in pdate.lower():
              pdate=date-timedelta(days=2)
              pdate=pdate.strftime('%d/%m/%Y')
              # print(f"Updated pdate after condition 3: {pdate}")
            elif '3' in pdate.lower():
              pdate=date-timedelta(days=3)
              pdate=pdate.strftime('%d/%m/%Y')
              # print(f"Updated pdate after condition 4: {pdate}")
            else:
              pdate = job.find('span', class_='sim-posted').span.text.strip()
              # print(f"Updated pdate after condition 5: {pdate}")

            site = job.header.h2.a['href']

            missing_details=missing_details_finder(site)

            jobId=missing_details["JobId Times Job"]

            jd = job.find('ul', class_='list-job-dtl clearfix').find_next('li').text.strip()

            skills = job.find('span', class_='srp-skills').text.replace(' ', '')
            # print(jobid_madeup)
            job_details = {
                    "Made Up JOB ID": jobid_madeup,
                    "Job Id TimesJob": jobId,
                    "Job Title": title.strip(),
                    "Company Name": comp.strip(),
                    "Required Skills": skills.strip(),
                    "Website Link": site,
                    "Posted on": pdate,
                    "Job Description": jd,
                    "Experience Required": exp_req,
                    "Job Location": job_location
                }
            job_list.append(job_details)
          except Exception as e:
            pass

    return job_list


def missing_details_finder(link):
  website2=requests.get(link)
  soup2=BeautifulSoup(website2.content,'lxml')
  # salary=soup2.find('ul',class_='top-jd-dtl clearfix').text
  # employment_type=soup2.find('li',string='Employment Type:').text
  try:
    jobId=soup2.find('div',class_='jd-jobid').text.replace("Job Id: ","")
  except AttributeError:
    pass
  job_details2={
      # "Salary": salary,
      # "Employment Type": employment_type,
      "JobId Times Job": jobId
  }
  return job_details2

def main_job():
    json_read_data=[]
    job_roles=['Digital Marketing', 'Copywriter','Content Writer','Social Media content writer','SEO Executive','Social Media Marketer','Content Strategist','Conceptualizer','UI UX Designer']
    # job_roles=['Digital Marketing', 'Copywriter','Content Writer']
    try:
      with open('timesjob.json','r') as f:
          json_read_data=f.read()
          json_read_data=json.loads(json_read_data)
          print(json_read_data)
          # print(type(json_read_data))
    except  FileNotFoundError:
      pass
    temp_data_storage=[]
    for job in job_roles:
      for i in range(0, 10):
        if i == 0:
            # url=f"https://www.timesjobs.com/candidate/job-search.html?searchName=recentSearches&from=submit&luceneResultSize=200&txtKeywords={quote(job)}&cboWorkExp1={work_exp}&postWeek=60&searchType=personalizedSearch&actualTxtKeywords={quote(job)}&searchBy=0&rdoOperator=OR&txtLocation={loc}&gadLink={quote(job)}"
            # url=f"https://www.timesjobs.com/candidate/job-search.html?searchName=recentSearches&from=submit&luceneResultSize=200&txtKeywords={quote(job)}&postWeek=60&searchType=personalizedSearch&actualTxtKeywords={quote(job)}&searchBy=0&rdoOperator=OR&gadLink={quote(job)}"
            url=f"https://www.timesjobs.com/candidate/job-search.html?searchName=recentSearches&from=submit&luceneResultSize=200&txtKeywords={quote(job)}&postWeek=3&searchType=personalizedSearch&actualTxtKeywords={quote(job)}&searchBy=0&rdoOperator=OR&gadLink={quote(job)}"
            print(url)
        elif i <11:
            # url=f"https://www.timesjobs.com/candidate/job-search.html?from=submit&luceneResultSize=200&txtKeywords={quote(job)}&cboWorkExp1={work_exp}&postWeek=60&searchType=personalizedSearch&actualTxtKeywords={quote(job)}&searchBy=0&rdoOperator=OR&txtLocation={loc}&pDate=I&sequence={i+1}&startPage=1"
            url=f"https://www.timesjobs.com/candidate/job-search.html?from=submit&luceneResultSize=200&txtKeywords={quote(job)}&postWeek=3&searchType=personalizedSearch&actualTxtKeywords={quote(job)}&searchBy=0&rdoOperator=OR&pDate=I&sequence={i+1}&startPage=1"
            print(url)

        website = requests.get(url)
        soup = BeautifulSoup(website.content, 'lxml')
        if json_read_data:
            data=find_jobs(soup,json_read_data)
        else:
            data=find_jobs(soup)
        temp_data_storage.extend(data)

    print(temp_data_storage)
    json_read_data.extend(temp_data_storage)
    json_data=json.dumps(json_read_data,indent=2)

    with open('timesjob.json','w') as f:
        f.write(json_data)

    with open('timesjob.json','r') as f:
      json_to_csv_data=f.read()
      json_to_csv_data=json.loads(json_to_csv_data)

    flattened_data = []
    for entry in json_to_csv_data:
        row = [
            entry["Made Up JOB ID"],
            entry["Job Id TimesJob"],
            entry["Job Title"],
            entry["Company Name"],
            entry["Required Skills"],
            entry["Website Link"],
            entry["Posted on"],
            entry["Job Description"],
            entry["Experience Required"],
            # entry["Salary"],
            entry["Job Location"],
            # entry["Employment Type"]
        ]
        flattened_data.append(row)

    with open('timesjob.csv', 'w', newline='', encoding='utf-8') as csvfile:
      csvwriter = csv.writer(csvfile)
      csvwriter.writerow([
           "Made Up JOB ID","Job ID TimesJob","Job Title", "Company Name", "Required Skills", "Website Link", "Posted on",
          "Job Description", "Experience Required", "Job Location"
      ])
      csvwriter.writerows(flattened_data)

    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
      "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name('job-scrapper-409509-6eb907a30cb1.json', scope)
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1QQZcFgAv5KhpmcUJ-zWob9QmEEVC3kXGDGHsoEoJwh8/edit#gid=1587694456')
    worksheet = spreadsheet.worksheet('TimesJob')
    header_to_write=[["Made Up JOB ID","Job Id TimesJob", "Job Title", "Company Name", "Required Skills", "Website Link", "Posted on",
        "Job Description", "Experience Required", "Job Location"]]
    data_to_write = header_to_write + [[item[header] for header in header_to_write[0]] for item in json_to_csv_data]
    worksheet.update(data_to_write)



# def nextpage(soup):
#     urlloc = soup.find('div', class_='srp-pagination clearfix')
#     url_link = urlloc.find_all('a', href=True)
#     for url in url_link:
#         onclick_value = url.get('onclick')
#         match = re.search(r'getNextPageResult\((\d+),(\d+)\)', onclick_value)
#         if match:
#             page_number = match.group(1)
#             other_parameter = match.group(2)

#             constructed_link = f"https://www.timesjobs.com/candidate/job-search.html?from=submit&luceneResultSize=200&txtKeywords=content%20copywriting&postWeek=60&searchType=personalizedSearch&actualTxtKeywords=content%20copywriting&searchName=recentSearches&searchBy=0&rdoOperator=OR&pDate=I&sequence={page_number}&startPage=1"
#             return constructed_link

if __name__ == '__main__':
    # schedule.every().day.at("11:56:00", timezone('Asia/Kolkata')).do(main_job)
    # while True:
    #   print(datetime.now(timezone_kolkata))
    #   schedule.run_pending()
    #   time.sleep(1)
    main_job()
