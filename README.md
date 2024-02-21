"#FindMyJob"

Neccessary Libraries:
* BeautifulSoup
* Requests
* time
* json
* urllib
* csv
* schedule
* gspread
* oauth2client
* datetime
* pytz

Websites Implemented:
* Naukri.com
* Foundit.com
* Internshala.com
* timesjob.com

Each code has three functions:
  * main_job(): This is the primary function which handles all the tasks. A list of jobs is hardcoded by the names job_roles. First it reads if already a file in present and if its present in the directory it reads the data and saves it in the variable json_read_data.
    Next a loop in present which iterates through all the job_roles on by one to scrape for jobs.
    requests library is used make requests to the websites which then saves the json data that is recieved ( HTML code in case of TimesJob and Internshala) and saves it in the variable json_data.
    It then passes the json-read data and json_data in the function find_jobs() which then returns a list of data which is appended in the variable temp_data_storage.
    This data in temp_data_storage in then appended to already read data of existing json doc in the variable json_read_data.
    Then the json document in opened in write mode and all the data is saved in it. Next the Json document in opened in read mode and data is saved in another variable which the write the data to CSV file and these documents are saved in the same directory as the
    running scripts.
    Then the spredsheet is opened using URL and which then opens the repective worksheets and writes the data in the sheet. It is scheduled to run everyday at 6:00 am (Kolkata timezone).

  * find_jobs(): This is the basic function which scrapes the website for the jobs. This is primarily called for the script to scrape the website and returns the job details of a particular job one by one. First it initializes the already existing jobid one by one if it     is already present. Next it runs a loop through every block of te json data which contains the data about indivisual jobs.Once all the data is fetched it is stored in dictionary and then one by one appended in the a list.

  * missing_details_finder(): This function in called from the function find_jobs() and it tries to find all the data that can't be found in the primary page by going into the job description page and returns the value as a dictionary to the function find_jobs(). The        returned values depend upon the missing details in the first page and differs from website to website.


USAGE:
* Each files should be ran individually for the first time and then as long as it is hosted it will run automatically every day at 6:00 am (Kolkata Timezone) everyday.

SETUP INSTRUCTION:
<!-- Create a virtual env -->
* python -m venv myenv
* myenv\Scripts\activate
* pip install -r requirements.txt
* With each script there should be a GoogleSheet API json document be present in the same directory which contains the api credentials. Code can be executed individually by running the python files by calling
 *python filename.py*


Ensure:
* Google drive and Google Sheet API Docs are present in the respective folders of each scripts.
* To save time and prevent timeOuts it is advised to have pre-saved documents of previous 3days of scraped data in the same folder as the script
* Ensure all the requirements are met and libraries present.
* Following Libraries Should be present:  beautifulsoup4==4.9.3
                                          requests==2.26.0
                                          time
                                          json
                                          re
                                          urllib
                                          csv
                                          schedule==1.1.0
                                          gspread==4.0.1
                                          oauth2client==4.1.3
                                          datetime
                                          pytz==2021.3

# Each script is called using the terminal by 'python filename.py' which will then look for following files:
  => filename.json
  => filename.csv
  => job-scrapper-409509-6eb907a30cb1.json
Ensure all these files are in the same folder.

After execution the script will paste all the data of the csv file in the Google sheet.
Link of the current Google Sheet: https://docs.google.com/spreadsheets/d/1QQZcFgAv5KhpmcUJ-zWob9QmEEVC3kXGDGHsoEoJwh8/edit
