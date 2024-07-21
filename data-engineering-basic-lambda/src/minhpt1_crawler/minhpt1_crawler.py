import pandas as pd
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from utils import get_info, load_to_s3

# event = {
#     'chromepath' : 'E:\DA\D4E\Spark\chromedriver-win64\chromedriver.exe',
#     "bucket_name": "ai4e-ap-southeast-1-dev-s3-data-landing",
#     "object_key": "minhpt1_test/raw_zone/vietnamworks_selenium.json"
# }


def lambda_handler(event,context):
    try:

        chromepath = event['chromepath']
        driver = webdriver.Chrome(executable_path=chromepath)

        page_still_valid = True
        page = 1
        df_job = []

        while page_still_valid:
            driver.get(f'https://www.vietnamworks.com/viec-lam?q=data-analyst&g=5&j=27&page={page}')
            time.sleep(10)

            # wait = WebDriverWait(driver, 5)
            # wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.sc-CCtys.dIROTF')))

            #scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            print(f'https://www.vietnamworks.com/viec-lam?q=data-analyst&g=5&j=27&page={page}')
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            ##Check if last page?
            try:
                if 'Hiện chưa có công việc nào theo tiêu chí bạn tìm' in soup.find('h2', class_='title').text.strip():
                    page_still_valid = False
            except Exception:
                pass

            job_containers = soup.find_all('div', class_="sc-CCtys dlROTF")

            for container in job_containers:
                url = container.find('a', target='_blank').get('href')
                info = get_info('https://www.vietnamworks.com'+ url)
                print(container.find('a', target='_blank').get('href'))

                df_job.append(info)

            page += 1
        driver.quit()

        return df_job 


    except Exception as ex:
        #error handling
        print(f'Error: {ex}')

    #load to s3
    bucket_name = event["bucket_name"]
    object_key = event["object_key"]

    df = pd.DataFrame(df_job)

    load_to_s3(df,bucket_name,object_key)