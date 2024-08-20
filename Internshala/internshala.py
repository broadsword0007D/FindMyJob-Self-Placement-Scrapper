#Email Implementation

#!pip install schedule
#!pip install gspread
#!pip install oauth2client
#!pip install pytz
from difflib import IS_LINE_JUNK
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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }


def find_jobs(soup,local_json_data=0):
  job_list=[]
  jobs=soup.find_all('div', class_='container-fluid individual_internship visibilityTrackerItem')
  # jobid_list=[]
  jobid_dict={}
  try:
    for id in local_json_data:
        id_data=id['Job Id Internshala']
        jobid_dict[id_data]='True'
    # print(jobid_dict)
  except TypeError:
    pass
  for job in jobs:
      idcounter=0
      job_link=job.h3.a['href']
      extra_details=missing_details_finder(f"https://internshala.com{job_link}")
      jobId=extra_details['Job ID']
      try:
        if jobid_dict[jobId]=="True":
          idcounter+=1
      except KeyError:
        pass

      if(idcounter==0):
        try:
          title=job.find('a',class_='view_detail_button').text

          company_name=job.find('a',class_='link_display_like_text view_detail_button').text.strip()
          try:
            if((job.find('div',class_='success_and_early_applicant_wrapper').find_next('div',class_='status status-small status-success').text),str):
              pdate=job.find('div',class_='success_and_early_applicant_wrapper').find_next('div',class_='status status-small status-success').text.strip()
          except Exception as e:
            pdate="Quite Old"

          date=datetime.now().date()
          if 'hours' in pdate.lower() or 'now' in pdate.lower() or 'today' in pdate.lower():
              pdate=date
              pdate=pdate.strftime('%d/%m/%Y')
              # print(f"Updated pdate after condition 1: {pdate}")
          elif  '1' in pdate.lower():
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
             continue
              # print(f"Updated pdate after condition 5: {pdate}")


          salary=job.find('span',class_='stipend').text.replace('₹','')

          employment_type=job.find('div',class_='other_label_container').find_next('div',class_='status status-small status-inactive').text

          location=job.find('a',class_='location_link view_detail_button').text

          jd=extra_details['Job Description']
          skills=extra_details['Skills']

          # if any(item in skills for item in skillsr):
          job_details = {
                          "Job Id Internshala": jobId,
                          "Job Title": title.strip(),
                          "Company Name": company_name.strip(),
                          "Required Skills": str(skills),
                          "Website Link": f"https://internshala.com{job_link}",
                          "Posted on": pdate,
                          # "Experience Required": f"{min_exp}-{max_exp} years",
                          "Salary":salary,
                          "Job Location": location,
                          "Employment Type": employment_type,
                          "Job Description": jd
                          }
          # print(job_details)
          job_list.append(job_details)
        except Exception as e:
          pass
  return job_list


def missing_details_finder(link):
    website2=requests.get(link,headers=header)
    soup2=BeautifulSoup(website2.content,'lxml')
    job_details={}
    skill_list=[]
    try:
      skills=soup2.find('div',class_='section_heading heading_5_5 skills_heading').find_next('div',class_='round_tabs_container')
      skills=skills.find_all('span',class_='round_tabs')
      for skill in skills:
        # all_skills=skills.find('span',class_='round_tabs').text
        all_skill=skill.text.lower()
        skill_list.append(all_skill)

      job_details['Skills'] = str(skill_list)
    except Exception as e:
        skill_list.append('No Skills Listed')
        job_details['Skills'] = str(skill_list)
        pass
    try:
      jd=soup2.find('div',class_='section_heading heading_5_5 about_heading').find_next('div',class_='text-container').text.strip()
      job_details['Job Description']=jd
    except AttributeError:
      job_details['Job Description']="None"
      pass

    try:
      internship_id=soup2.find('div',class_='container-fluid individual_internship visibilityTrackerItem')
      internship_id=internship_id.get('internshipid') 
      job_details['Job ID']=internship_id
    except AttributeError:
      job_details['Job ID']="#"

    return job_details

def main_job():
  job_roles=['Digital Marketing', 'Copywriter','Content Writer','Social Media content writer','SEO Executive','Social Media Marketer','Content Strategist','Conceptualizer','UI UX Designer']
  json_read_data=[]
  temp_data_storage=[]
  try:
    with open('internshala.json','r') as f:
        json_read_data=f.read()
        json_read_data=json.loads(json_read_data)
        # print(type(json_read_data))
  except  FileNotFoundError:
    pass
  for job in job_roles:
    for i in range (1,20):
      if(i==1):
        # url=f'https://internshala.com/internships/keywords-{job.replace(" ","-")}/'
        # url=f"https://internshala.com/internships/{designation}-internship-in-{location}/"
        url=f'''https://internshala.com/internships/{job.replace(" ","-")}-internship/early-applicant-25/'''
        # print(url)
      else:
        url=f'''https://internshala.com/internships/{job.replace(" ","-")}-internship/early-applicant-25/page-{i}/'''
        # url=f"https://internshala.com/internships/{designation}-internship-in-{location}/page-{i}/"
        # url=f'https://internshala.com/internships/keywords-{job.replace(" ","-")}/page-{i}/'
        # print(url)
      website=requests.get(url,headers=header)
      soup=BeautifulSoup(website.content,'lxml')
      if json_read_data:
          data=find_jobs(soup,json_read_data)
      else:
          data=find_jobs(soup)
      temp_data_storage.extend(data)

  json_read_data.extend(temp_data_storage)
  json_data=json.dumps(json_read_data,indent=2)

  with open('internshala.json','w') as f:
        f.write(json_data)

  with open('internshala.json','r') as f:
      json_to_csv_data=f.read()
      json_to_csv_data=json.loads(json_to_csv_data)

  flattened_data = []
  for entry in json_to_csv_data:
      row = [
          entry["Job Id Internshala"],
          entry["Job Title"],
          entry["Company Name"],
          entry["Required Skills"],
          entry["Website Link"],
          entry["Posted on"],
          entry["Job Description"],
          entry["Salary"],
          entry["Job Location"],
          entry["Employment Type"]
      ]
      flattened_data.append(row)

  with open('internshala Jobs.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow([
        "Job ID Internshala","Job Title", "Company Name", "Required Skills", "Website Link", "Posted on",
        "Job Description", "Job Location", "Salary","Employment Type"
    ])
    csvwriter.writerows(flattened_data)
    print("Data Updated in the local CSV file")

  scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
      "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

  credentials = ServiceAccountCredentials.from_json_keyfile_name('job-scrapper-409509-6eb907a30cb1.json', scope)
  client = gspread.authorize(credentials)

  spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1QQZcFgAv5KhpmcUJ-zWob9QmEEVC3kXGDGHsoEoJwh8/edit#gid=876037302')
  worksheet = spreadsheet.worksheet('Internshala')
  header_to_write=[["Job Id Internshala", "Job Title", "Company Name", "Required Skills", "Website Link", "Posted on",
        "Job Description", "Salary", "Job Location","Employment Type"]]
  data_to_write = header_to_write + [[item[header] for header in header_to_write[0]] for item in json_to_csv_data]
  worksheet.update(data_to_write)
  print("Data writen in the Google Sheet")

if __name__=="__main__":
    # schedule.every().day.at("06:00:00", timezone('Asia/Kolkata')).do(main_job)
    # while True:
    #   # print(datetime.now(timezone_kolkata))
    #   schedule.run_pending()
    #   time.sleep(1)
   main_job()
