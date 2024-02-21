#Api Implementation
# !pip install schedule
# !pip install gspread
# !pip install oauth2client
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
import pytz
from pytz import timezone

timezone_kolkata = pytz.timezone('Asia/Kolkata')

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Referer':'https://www.foundit.in/srp/results?query=python&searchId=188a4457-4277-4815-ab65-dcb42df6ba31',
    'Cookie': 'MSUID=da360e97-da77-4c42-8f66-a58425ee0c9d; NHP=true; WZRK_G=e2111b9b559643d4b33c3126d20cccac; _gcl_au=1.1.672930201.1702448425; ajs_anonymous_id=%2218c61d5673238f-0937f36c2a7df-26001951-1fa400-18c61d5673313ab%22; _ga=GA1.1.1016041713.1702448425; adb=0; ufi=1; uuidAB=820ab5dc-ae70-43bf-8549-8bc64fc08221; _clck=ghe2yp%7C2%7Cfhk%7C0%7C1442; _uetsid=b3975b10997f11eea5fca320490eb3b5; _uetvid=b39759a0997f11eeab50eb648f242224; cto_bundle=4Xlkw185N3pUbSUyQm5vbmptcnpQNnJ5JTJCdks0NWtubVFmdkJUMlUlMkJjejlVdEZHWkJpMGFVbXBpejlyUDExYmVvUHNNZVRFd2NZM28yMVJrZTBZZnQxN24lMkJWJTJCSXRkNUhyRkk2cklHMFFDMUklMkJWZlJ6eWpDOVdKTTMxMSUyQjFPenpzQ1ZZT0hqZHRodnZtdTFFRlZqNEg0bEkzVjFaUSUzRCUzRA; _clsk=jrdlvm%7C1702633842990%7C4%7C1%7Cw.clarity.ms%2Fcollect; RT="z=1&dm=www.foundit.in&si=7d5d7b53-22f5-4524-8482-cd726eaaa25a&ss=lq6g2ttg&sl=3&tt=tch&obo=2&rl=1&ld=10uz0&r=1jfxgn9z&ul=10uz0&hd=10yo1"; _ga_HT3XNW7GHL=GS1.1.1702633596.8.1.1702635314.60.0.0',
    'Accept-Encoding': 'gzip, deflate, br'
    }

header2 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
# skillsr=['']
# skillsgth=[]

def find_jobs(json_data_to_be_passed,local_json_data=0):
  job_list=[]
  jobid_dict={}
  try:
    for id in local_json_data:
        id_data=id['Job Id Foundit']
        jobid_dict[id_data]="True"
  except TypeError:
    pass
  for job in json_data_to_be_passed["jobSearchResponse"]["data"]:
      jobId=job.get("jobId",0)
      idcounter=0
      try:
        if jobid_dict[jobId]=="True":
          idcounter+=1
      except KeyError:
        pass
      if(idcounter==0) and (jobId!=0):
        # print(jobId)
        try:
          title=job.get("title", "N/A")

          job_location=job.get("locations","N/A")
          # min_exp=job.get("minimumExperience","N/A").get("years","N/A")
          min_exp_data = job.get("minimumExperience")

          max_exp_data = job.get("maximumExperience")

          if isinstance(min_exp_data, dict):
                min_exp = min_exp_data.get("years", "N/A")
          else:
                min_exp = "N/A"
          if isinstance(max_exp_data, dict):
                max_exp = max_exp_data.get("years", "N/A")
          else:
                max_exp = "N/A"

          employment_type=job.get("employmentTypes","N/A")

          company_name=job.get("companyName","N/A")

          if "redirectUrl" in job and job["redirectUrl"]:
            job_link=job.get("redirectUrl")
          elif "seoJdUrl" in job:
            job_link=f"www.foundit.in{job.get('seoJdUrl')}"
          elif "seoCompanyUrl" in job:
            job_link=job.get("seoCompanyUrl")
          else:
            job_link="N/A"

          skills=job.get("skills","N/A")
          pdate=job.get("postedBy","N/A").strip()
          date=datetime.now().date()
          if 'hours' in pdate.lower():
              pdate=date
              pdate=pdate.strftime('%d/%m/%Y')
              # print(f"Updated pdate after condition 1: {pdate}")
          elif 'day' in pdate.lower() or '1' in pdate.lower():
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


          min_salary_data=job.get("minimumSalary")
          max_salary_data=job.get("maximumSalary")
          if isinstance(min_salary_data, dict):
                min_salary = min_salary_data.get("absoluteValue", "N/A")
          else:
                min_salary = "N/A"
          if isinstance(max_salary_data, dict):
                max_salary = max_salary_data.get("absoluteValue", "N/A")
          else:
                max_salary = "N/A"

          if isinstance(job.get('seoJdUrl'),str):
            extra_details=missing_details_finder(f"https://www.foundit.in{job.get('seoJdUrl')}")
          elif(job.get('seoJdUrl')=='none'):
            pass

          jd=extra_details.get("Job Description","N/A")
          job_details = {
                      "Job Id Foundit": jobId,
                      "Job Title": title.strip(),
                      "Company Name": company_name.strip(),
                      "Required Skills": skills.strip(),
                      "Website Link": job_link,
                      "Posted on": pdate,
                      "Job Description":jd,
                      "Experience Required": f"{min_exp}-{max_exp} years",
                      "Salary":f"{min_salary}-{max_salary}",
                      "Job Location": job_location,
                      "Employment Type": str(employment_type)
                  }
          job_list.append(job_details)
          # print("Data Apending")
        except Exception as e:
          pass
  return job_list

def missing_details_finder(link):
    website2=requests.get(link,headers=header)
    soup2=BeautifulSoup(website2.content,'lxml')

    # jd=soup.find('div',class_='jobDescription').text
    jd=soup2.find('div',class_='about-company').text.replace('\n',' ')

    job_details={
        "Job Description": jd
    }
    return job_details


def main_job():
  job_roles=['Digital Marketing', 'Copywriter','Content Writer','Social Media content writer','SEO Executive','Social Media Marketer','Content Strategist','Conceptualizer','UI UX Designer']
  json_read_data=[]
  try:
    with open('foundit.json','r') as f:
        json_read_data=f.read()
        json_read_data=json.loads(json_read_data)
  except  FileNotFoundError:
    pass
  temp_data_storage=[]
  for job in job_roles:
    start_index=100
    for i in range(1,11):
      if(i==1):
          # url=f"https://www.foundit.in/middleware/jobsearch?sort=1&limit=100&query=p{job.replace(' ','-')}&locations={job_location}&experienceRanges={applicant_exp}~{applicant_exp}&experience={applicant_exp}"
          # url=f"https://www.foundit.in/middleware/jobsearch?sort=1&limit=100&query={job.replace(' ','-')}&queryDerived=true&jobFreshness=3"
          url=f"https://www.foundit.in/middleware/jobsearch?sort=1&limit=100&query={quote(job)}&queryDerived=true&jobFreshness=3"
          # print(url)

      else:
          # url=f"https://www.foundit.in/middleware/jobsearch?start={start_index}&sort=1&limit=100&query={job.replace(' ','-')}&locations={job_location}&experienceRanges={applicant_exp}~{applicant_exp}&experience={applicant_exp}&queryDerived=true"
          # url=f"https://www.foundit.in/middleware/jobsearch?start={start_index}&sort=1&limit=100&query={job.replace(' ','-')}&queryDerived=true&jobFreshness=3"
          url=f"https://www.foundit.in/middleware/jobsearch?start={start_index}&sort=1&limit=100&query={quote(job)}&queryDerived=true&jobFreshness=3"
          # print(url)
          start_index+=100

      website=requests.get(url,headers=header)
      json_data=website.json()
      if json_read_data:
          data=find_jobs(json_data,json_read_data)
      else:
          data=find_jobs(json_data)
      temp_data_storage.extend(data)
      json_data_fetch=json.dumps(data,indent=2)

  json_read_data.extend(temp_data_storage)
  json_data=json.dumps(json_read_data,indent=2)

  with open('foundit.json','w') as f:
    f.write(json_data)

  with open('foundit.json','r') as f:
      json_to_csv_data=f.read()
      json_to_csv_data=json.loads(json_to_csv_data)

  flattened_data = []
  for entry in json_to_csv_data:
      row = [
          entry["Job Id Foundit"],
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

  with open('Foundit Jobs.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow([
        "Job Id Foundit","Job Title", "Company Name", "Required Skills", "Website Link", "Posted on",
        "Job Description", "Experience Required", "Salary", "Job Location",
        "Employment Type"
    ])

    csvwriter.writerows(flattened_data)
    print("Data Updated in the local CSV file")
  scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
  "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

  credentials = ServiceAccountCredentials.from_json_keyfile_name('job-scrapper-409509-6eb907a30cb1.json', scope)
  client = gspread.authorize(credentials)

  spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1QQZcFgAv5KhpmcUJ-zWob9QmEEVC3kXGDGHsoEoJwh8/edit#gid=1327941625')
  worksheet = spreadsheet.worksheet('FoundIt')
  header_to_write=[["Job Id Foundit", "Job Title", "Company Name", "Required Skills", "Website Link", "Posted on",
        "Job Description", "Experience Required", "Salary", "Job Location","Employment Type"]]
  data_to_write = header_to_write + [[item[header] for header in header_to_write[0]] for item in json_to_csv_data]
  worksheet.update(data_to_write)
  print("Data writen in the Google Sheet")


if __name__=="__main__":
  # print(datetime.now(timezone_kolkata))
  # schedule.every().day.at("06:00:00", timezone('Asia/Kolkata')).do(main_job)
  # while True:
  #   print(datetime.now(timezone_kolkata))
  #   schedule.run_pending()
  #   time.sleep(1)
  main_job()
