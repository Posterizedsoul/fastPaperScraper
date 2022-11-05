import os
import time
import lxml
import requests
from multiprocessing.pool import ThreadPool
from functools import partial
from bs4 import BeautifulSoup
import re
from PyPDF2 import PdfFileReader
from typing import Optional
from typing import Literal

def fetch_subject_list():
    subject_dict = {}
    r = requests.get('https://papers.gceguide.com/A%20Levels/')
    soup = BeautifulSoup(r.text, 'lxml')
    for link in soup.find_all('a', class_='name'): 
        sub_code = re.findall('\(([^)]+)\)',link.text)[-1]
        sub_name = link.text
        subject_dict.update({sub_code:sub_name})
    # print(subject_dict)
    return subject_dict
# fetch_subject_list()

def return_subject_url(subject_code:int):
    sub_dict = fetch_subject_list() 
    if sub_dict[f'{subject_code}'] is not None:
        url = 'https://papers.gceguide.com/A%20Levels/' + sub_dict[f'{subject_code}'].replace(' ', '%20')
    else:
        print("Enter a Valid Subject Code")
    print(url)
    return url
# return_subject_url(9708)

def downloader(sub_code:int, year_from_to:str, paper_code:int,season:Literal["s", "w"] = "s", paper_type:Literal["qp", "ms"] ="qp"):
    '''
    Format for Subject code -> "9702",Format for year_from_to -> "2020-2022" where (former date)-(final date to download including the given date)    
    season -> "s" for summer and "w" for winter
    paper_type -> 
                    PAPER_TERMS = {
                        'qp':'QP',
                        'ir':'IR',
                        'ms':'MS',
                        'er':'ER'
                    }
    '''

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    SUB_URL = return_subject_url(sub_code)
    
    def return_valid_date(year_from_to=year_from_to):
        start_date = year_from_to.split("-")[0]
        end_date = year_from_to.split("-")[1]
        _temp_date = start_date
        inbetween_dates = [(int(_temp_date)+i) for i in range(int(end_date) - (int(start_date)-1))]
        return start_date, end_date, inbetween_dates
    return_valid_date()
    
    def return_sub_url_with_date():
        start_date, end_date, inbetween_dates = return_valid_date()
        if inbetween_dates:
            '''
            To get -> https://papers.gceguide.com/A%20Levels/Mathematics%20-%20Further%20(9231)/2021/9231_w21_qp_41.pdf
            Url (getting) -> https://papers.gceguide.com/A%20Levels/Mathematics%20(9709)            
            '''
            date_url_list = [SUB_URL+f"/{date}/{sub_code}_{season}{str(date)[-2:]}_{paper_type}_{paper_code}.pdf" for date in inbetween_dates]
            print(date_url_list)
        else: 
            print("No inbetween_dates")
            # url_list = []
        return date_url_list
    
    def create_directory():
        dir_name = fetch_subject_list()[f'{sub_code}']
        dir_list = [ item for item in os.listdir(ROOT_DIR) if os.path.isdir(os.path.join(ROOT_DIR, item)) ]
        os.chdir(ROOT_DIR)

        if not dir_name in dir_list:
            os.mkdir(dir_name)
            os.chdir(dir_name)
            dir_list = os.listdir()
            
            os.mkdir(paper_type.upper())
            os.chdir(paper_type.upper())

            print(f"Made dir with name {dir_name} and changed current directory to {dir_name}")
            print(f"dir list inside dir --> {dir_name} is {dir_list}")
        else: 
            print(os.listdir())
            os.chdir(ROOT_DIR)
            os.chdir(dir_name)
            dir_list = os.listdir()
            if not paper_type.upper() in dir_list:
                os.mkdir(paper_type.upper())
                os.chdir(paper_type.upper())
                print(f"changed to {paper_type.upper()}")
            else:
                os.chdir(paper_type.upper())
                print(f"changed to {paper_type.upper()}")
            print(f"dir list inside dir --> {dir_name} is {dir_list}")
            print(f"Changed to dir {os.getcwd()}")


    def multi_threaded_downloader(url):
            
        create_directory()
        file_name = url.split("/")[-1]
        print(file_name)
        r = requests.get(url, stream=True)
        if r.status_code == requests.codes.ok:
            with open(file_name, 'wb') as f:
                for data in r:
                    f.write(data)
    results = ThreadPool(5).imap_unordered(multi_threaded_downloader, return_sub_url_with_date())
    for r in results:
        print(r)
downloader("9231", "2020-2022", 21)

'''
To do 
-> Make system to download entirity of papers themselves
-> Make system to crop exact questions
'''

