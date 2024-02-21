#!pip install schedule
#!pip install gspread
#!pip install oauth2client
#!pip install pytz

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


header={
    'AppId': '109',
    'SystemId':'Naukri'
}
header2={
    'AppId': '121',
    'SystemId':'Naukri'
}

timezone_kolkata = pytz.timezone('Asia/Kolkata')

def find_jobs(json_data_to_be_passed,skillsr,local_json_data=0):
  job_list=[]
  jobid_dict={}
  try:
    for id in local_json_data:
      id_data=id['Job ID Naukri']
      jobid_dict[id_data]="True"
  except TypeError:
    pass

  for job in json_data_to_be_passed.get("jobDetails",[]):
    idcounter=0
    jobId= job.get("jobId",0)
    # print(jobId)
    try:
      if jobid_dict[jobId]=="True":
          idcounter+=1
    except Exception as e:
      pass
    if (idcounter==0):
      try:
          title=job.get("title","N/A")

          pdate=str(job.get("footerPlaceholderLabel","N/A").strip())
          date=datetime.now().date()
          if 'today' in pdate.lower() or 'just now' in pdate.lower() or "minute" in pdate.lower() or "hour" in pdate.lower() or "hours" in pdate.lower():
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
            pdate=str(job.get("footerPlaceholderLabel","N/A"))
            # print(f"Updated pdate after condition 5: {pdate}")

          company_name=job.get("companyName","N/A")

          skills=job.get("tagsAndSkills","N/A")

          job_url=f"www.naukri.com{job.get('jdURL', 'N/A')}"

          for location in job.get("placeholders",[]):
            if(location["type"]=="location"):
              job_location=location.get("label","N/A")

          for exp in job.get("placeholders",[]):
            if(exp["type"]=="experience"):
              exp_required=exp.get("label","N/A")

          for salary in job.get("placeholders",[]):
            if(salary["type"]=="salary"):
              job_salary=salary.get("label","N/A")

          jd=job.get("jobDescription","N/A").strip()
          soup=BeautifulSoup(jd,'lxml')
          jd=soup.get_text(separator=' ').strip()
          extra_details=missing_details_finder(f"https://www.naukri.com/jobapi/v4/job/{jobId}?microsite=n&src=jobsearchDesk&sid={json_data_to_be_passed.get('sid')}&xp=1&px=1")

          employment_type=extra_details.get("Employment Type",'N/A')

          # mskillsr = [mandatory.replace(' ', '').lower() for mandatory in skillsr]
          # mskillsgth = [optional.replace(' ', '').lower() for optional in skillsgth]
          # mandatory = any(mandatory.lower() in skills.lower() for mandatory in mskillsr)
          # optional = any(optional.lower() in skills.lower() for optional in mskillsgth)
          if (jobId!=0):
              job_details = {
                        "Job ID Naukri": jobId,
                        "Job Title": title.strip(),
                        "Company Name": company_name.strip(),
                        "Required Skills": skills.strip(),
                        "Website Link": job_url,
                        "Posted on": pdate,
                        "Job Description": jd,
                        "Experience Required": exp_required,
                        "Salary": job_salary,
                        "Job Location": job_location,
                        "Employment Type":employment_type
                    }
              # job_details.update(extra_details)
              job_list.append(job_details)
      except Exception as e:
            pass
  return job_list


def missing_details_finder(link):
  website2=requests.get(link,headers=header2)
  json_data2=website2.json()
  employment_type=json_data2['jobDetails']['employmentType']
  job_details={
        "Employment Type": employment_type
      }
  return job_details

def main_job():
  skillsr = ['']
  skillsgth = []
  json_read_data=[]
  temp_data_storage=[]
  job_roles=['Digital Marketing', 'Copywriter','Content Writer','Social Media content writer','SEO Executive','Social Media Marketer','Content Strategist','Conceptualizer','UI UX Designer']
  try:
    with open('naukri.json','r') as f:
        json_read_data=f.read()
        json_read_data=json.loads(json_read_data)
        # print(json_read_data)
        # print(type(json_read_data))
  except  FileNotFoundError:
    pass
  for job in job_roles:
    for i in range(1,11):
        # website=requests.get(f'https://www.naukri.com/jobapi/v3/search?noOfResults=100&urlType=search_by_key_loc&searchType=adv&location={loc}&keyword={quote(job)}&pageNo={i}&experience={applicant_exp}&k={quote(job)}&l={loc}&experience={applicant_exp}&nignbevent_src=jobsearchDeskGNB&seoKey={job.replace(" ","-")}-jobs-in-{loc}&src=jobsearchDesk&latLong=',headers=header)
        website=requests.get(f'https://www.naukri.com/jobapi/v3/search?noOfResults=100&urlType=search_by_keyword&searchType=adv&&keyword={quote(job)}&pageNo={i}&jobAge=3&k={quote(job)}&nignbevent_src=jobsearchDeskGNB&jobAge=3&seoKey={job.replace(" ","-")}-jobs&src=jobsearchDesk&latLong=',headers=header)
        json_data=website.json()
        if json_read_data:
            data=find_jobs(json_data,skillsr,json_read_data)
        else:
            data=find_jobs(json_data,skillsr)
        temp_data_storage.extend(data)

  json_read_data.extend(temp_data_storage)
  json_data=json.dumps(json_read_data,indent=2)

  with open('naukri.json','w') as f:
    f.write(json_data)

  with open('naukri.json','r') as f:
      json_to_csv_data=f.read()
      json_to_csv_data=json.loads(json_to_csv_data)

  flattened_data = []
  for entry in json_to_csv_data:
      row = [
          entry["Job ID Naukri"],
          entry["Job Title"],
          entry["Company Name"],
          entry["Required Skills"],
          entry["Website Link"],
          entry["Posted on"],
          entry["Job Description"],
          entry["Experience Required"],
          entry["Salary"],
          entry["Job Location"],
          entry["Employment Type"]
      ]
      flattened_data.append(row)

  with open('Naukri Jobs.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow([
       "Job ID Naukri", "Job Title", "Company Name", "Required Skills", "Website Link", "Posted on",
        "Job Description", "Experience Required", "Salary", "Job Location","Employment Type"
    ])

    csvwriter.writerows(flattened_data)
    print("Data Updated in the local CSV file")
  scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
  "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

  credentials = ServiceAccountCredentials.from_json_keyfile_name('job-scrapper-409509-6eb907a30cb1.json', scope)
  client = gspread.authorize(credentials)

  # spreadsheet = client.open('FindMyJobs').sheet2
  spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1QQZcFgAv5KhpmcUJ-zWob9QmEEVC3kXGDGHsoEoJwh8/edit')
  worksheet = spreadsheet.worksheet('Naukri')
  header_to_write=[["Job ID Naukri", "Job Title", "Company Name", "Required Skills", "Website Link", "Posted on",
        "Job Description", "Experience Required", "Salary", "Job Location","Employment Type"]]
  data_to_write = header_to_write + [[item[header] for header in header_to_write[0]] for item in json_to_csv_data]
  worksheet.update(data_to_write)
  print("Data writen in the Google Sheet")


if __name__=='__main__':
  # print(datetime.now(timezone_kolkata))
  # schedule.every().day.at("06:00:00", timezone('Asia/Kolkata')).do(main_job)
  # while True:
  #   schedule.run_pending()
  #   time.sleep(1)
   main_job()
