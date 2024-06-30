
############### 메인비즈 ##################

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import import_ipynb
from date_time import get_first_and_last_day_of_previous_month
import warnings


warnings.filterwarnings('ignore')

first_day_of_previous_month,  last_day_of_previous_month= get_first_and_last_day_of_previous_month()
formatted_date = first_day_of_previous_month.strftime('%Y%m')

year=first_day_of_previous_month.year
month=first_day_of_previous_month.month

# 웹페이지 URL
url = "https://www.smes.go.kr/mainbiz/usr/board/comData.do"

# GET 요청 보내기
response = requests.get(url)
if response.status_code == 200:
    # HTML 파싱
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 제목에 전월 기준이 포함된 링크 찾기
    links = soup.find_all('a')
    detail_page_url = None
    for link in links:
        if f"{year}년 {month}월말 기준 메인비즈 기업 현황" in link.text:
            detail_page_url = link.get('href')
            break
    
    if detail_page_url:
        detail_page_full_url = f"https://www.smes.go.kr{detail_page_url}"
        print("상세 페이지 링크:", detail_page_full_url)
        
        # 상세 페이지 요청 보내기
        detail_response = requests.get(detail_page_full_url)
        if detail_response.status_code == 200:
            detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
            
            # 첨부파일 링크 찾기
            attachment = detail_soup.find('a', class_='attach_file')
            if attachment and 'href' in attachment.attrs:
                download_link = attachment['href']
                download_url = f"https://www.smes.go.kr{download_link}"
                print("첨부파일 다운로드 링크:", download_url)
                
                # 첨부파일 다운로드
                file_response = requests.get(download_url)
                if file_response.status_code == 200:
                    with open('Data/mainbiz_download.xlsx', 'wb') as file:
                        file.write(file_response.content)
                    print("엑셀 파일 다운로드 완료")

                    df = pd.read_excel('Data/mainbiz_download.xlsx')
                
                    df.insert(0, 'GB', '003')
                    df2=df.drop(columns=['번호'])
                    df2.to_csv(f'Data/003_Mainbiz_{formatted_date}.csv', index=False, sep=',')
                else:
                    print("첨부파일 다운로드 실패:", file_response.status_code)
            else:
                print("첨부파일 링크를 찾을 수 없습니다.")
        else:
            print("상세 페이지 요청 실패:", detail_response.status_code)
    else:
        print("전월 기준이 포함된 제목을 찾을 수 없습니다.")
else:
    print("웹페이지 요청 실패:", response.status_code)


