from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import json
import boto3



def get_info(url):
    job_description = None
    job_requirement = None

    driver.get(url)

    wait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.sc-b8164b97-1.fkbCtV.vnwLayout__container')))

    time.sleep(0.5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    job_title = soup.find('h1', class_='sc-df6f4dcb-0 bsKseP').text.strip()

    company_name = soup.find('a', class_='sc-df6f4dcb-0 dIdfPh sc-f0821106-0 gWSkfE').text.strip()

    deadline = soup.find('span', class_='sc-df6f4dcb-0 bgAmOO').text.strip()

    salary = soup.find('span', class_ = 'sc-df6f4dcb-0 iOaLcj').text.strip()

    location = soup.find('div', class_='sc-a137b890-1 joxJgK').text.strip()

    job_detail = soup.find_all('div', class_='sc-4913d170-4 jSVTbX')

    for detail in job_detail:
        if 'Mô tả công việc' == detail.find('h2', class_ = 'sc-4913d170-5 kKmzVC').text.strip():
            job_description = detail.find('div', class_='sc-4913d170-6 hlTVkb').text.strip()
        elif 'Yêu cầu công việc' == detail.find('h2', class_ = 'sc-4913d170-5 kKmzVC').text.strip():
            job_requirement = detail.find('div', class_='sc-4913d170-6 hlTVkb').text.strip()


    #lấy quyền lợi
    benefits = soup.find_all('div', class_='sc-c683181c-2 fGxLZh')
    benefit = ''
    for i in benefits:
        benefit += '-' + i.text.strip()


    fields = []
    result = {
            'Job Title': job_title,
            'Company Name': company_name,
            'Hạn nộp hồ sơ': deadline,
            'Mức lương': salary,
            'Mô tả công việc': job_description,
            'Yêu cầu ứng viên': job_requirement,
            'Quyền lợi': benefit,
            'Địa điểm làm việc': location,
            'Lĩnh vực': fields,
            'Url': url
            }
    return result




def load_to_s3(df,bucket_name,object_key):
    df_results = []

    for index, row in df.iterrows():
        df_result = row.to_dict()
        df_results.append(df_result)

    #save result to s3
    s3_resource = boto3.resource('s3')
    s3_object = s3_resource.Object(bucket_name,object_key)

    s3_object.put(
        Body=(bytes(json.dumps(df_results, default=str).encode('UTF-8')))
    )
