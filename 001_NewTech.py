
############### 건설신기술 ##################

import requests
from bs4 import BeautifulSoup
import pandas as pd
import import_ipynb
from date_time import get_first_and_last_day_of_previous_month
import warnings

first_day_of_previous_month,  last_day_of_previous_month= get_first_and_last_day_of_previous_month()
formatted_date = first_day_of_previous_month.strftime('%Y%m')


warnings.filterwarnings('ignore')

# 기술 목록 페이지 URL
url = "https://www.kaia.re.kr/portal/newtec/comparelist.do?menuNo=200076"

# 웹사이트에 요청
response = requests.get(url)
response.raise_for_status()

# BeautifulSoup을 사용하여 HTML 콘텐츠 파싱
soup = BeautifulSoup(response.content, 'html.parser')

# 기술 목록을 포함하는 테이블의 모든 행 찾기
rows = soup.find_all('tr')

# 행 데이터 추출 및 상세 페이지에서 법인명과 주소 스크래핑
result=[]
for row in rows:
    title_tag = row.find('td', {'class': 't_subject'})
    if title_tag and title_tag.a:
        title = title_tag.a.get_text(strip=True)
        link = "https://www.kaia.re.kr" + title_tag.a['href']  # 링크를 가져와서 상세 페이지로 이동

        # 상세 페이지 요청 및 파싱
        detail_response = requests.get(link)
        detail_response.raise_for_status()
        detail_soup = BeautifulSoup(detail_response.content, 'html.parser')

        ######### 기본 정보 ##########
        date_header = detail_soup.find('th', text='고시일자')

        # 해당 행의 다음 <td> 태그의 텍스트 추출
        if date_header:
            date = date_header.find_next('td').get_text(strip=True)
        
        ######### 개발 정보 ##########
        developer_header =  detail_soup.find('h4', text='개발자')

        # <h4>개발자</h4> 다음에 오는 <table> 태그 찾기
        developer_table = developer_header.find_next('table')

        # <tbody> 안의 모든 행(tr) 찾기
        rows = developer_table.find('tbody').find_all('tr')
        
        output = []
        for row in rows:
            columns = row.find_all('td')
            if len(columns) > 1:
                sequence_number = columns[0].get_text(strip=True)
                company_name = columns[1].get_text(strip=True)
                company_address = columns[3].get_text(strip=True)
                output.append(f"{sequence_number}, {company_name}, {company_address}, {date}")

        result.append(output)

final=[]
for i in result:
    for j in i:
        final.append(j)

df = pd.DataFrame([x.split(', ')[1:] for x in final], columns=[ 'Company Name', 'Company Address', 'Date'])
df['Date'] = pd.to_datetime(df['Date'])

filtered_df = df[(df['Date'] >= first_day_of_previous_month) & (df['Date'] <= last_day_of_previous_month)]
filtered_df.insert(0, 'GB', '001')

filtered_df.to_csv(f'001_NewTech_{formatted_date}.csv', index=False, encoding='utf-8-sig')
