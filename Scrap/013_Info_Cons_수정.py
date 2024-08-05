############### 정보통신관리협회 ##################

import requests
from bs4 import BeautifulSoup
import pandas as pd
import warnings
import re

warnings.filterwarnings('ignore')


Directory='Data'

def fetch_data(url, page):
    
    params = {
    'searchSido': '',
    'searchType': '1',
    'searchText': '',
    'size': '10',
    'CSRFToken': 'bc41ee69-60f4-43a0-80de-ce5de606ff2d',
    'pageNumber':page,
    'v': '1717689012731'
    }
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
    
    response = session.get('https://ictis.kica.or.kr/construct/compList',timeout=30, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    text= soup.get_text()
    
    pattern = re.compile(r'\{[^{}]*\}')
    all_text=pattern.findall(text)
    
    # 각 객체의 키-값 쌍을 분리하여 데이터 프레임에 로드
    data = []
    for item in all_text:
        # 현재 객체의 모든 키-값 쌍을 추출
        key_values = re.findall(r'\"(\w+)\":\"?([^",]*)\"?', item)
        data_dict = {kv[0]: kv[1] for kv in key_values}
        data.append(data_dict)
        
    df=pd.DataFrame(data)

    return df['registNo']

i=1
result_df_f=[]
url='https://ictis.kica.or.kr/construct/compList'

result_df = fetch_data(url, i)
while fetch_data(url, i).columns[0]!='list':
    result_df = fetch_data(url, i)
    result_df_f.append(result_df)
    i=i+1


    # 웹 페이지 URL 설정
    detail_url = 'https://ictis.kica.or.kr/construct/assessment/announcement#searchSido=&baseYear=2024&searchType=1&searchText=&pageNumber=1&size=10'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    # 데이터를 저장할 빈 리스트 생성
    company_data = []
    
    # requests를 사용하여 웹 페이지에서 HTML 가져오기
    response = requests.get(detail_url, headers=headers)
    data = response.text
    
    # BeautifulSoup 객체 생성
    soup = BeautifulSoup(data, 'html.parser')
    
    for registNo in reg_no:
    
        # 상세 페이지 URL
        detail_url = f'https://ictis.kica.or.kr/construct/assessment/compDetail/{registNo}'
        response = requests.get(detail_url, headers=headers)
    
        if response.status_code == 200:
            detail_soup = BeautifulSoup(response.text, 'html.parser')
            
            try:
                company_name = detail_soup.find('th', text='상호').find_next_sibling('td').text.strip()
                business_number = detail_soup.find('th', text='사업자번호').find_next_sibling('td').text.strip()
                representative = detail_soup.find('th', text='대표자').find_next_sibling('td').text.strip()
                address = detail_soup.find('th', text='주소').find_next_sibling('td').text.strip()
                telno = detail_soup.find('th', text='전화번호').find_next_sibling('td').text.strip()
                amt = detail_soup.find_all('th')[18].find_next_sibling('td').text #시공능력평가액
                rank = detail_soup.find_all('th')[19].find_next_sibling('td').text #시공능력평가액 순위
    
                # 데이터 추가
                company_data.append({
                    'Company ID': registNo,
                    'Company Name': company_name,
                    'Business Number': business_number,
                    'Representative': representative,
                    'Address': address,
                    'Telno': telno,
                    'Evaluation Amount': amt,
                    'Rank': rank
                })
            except AttributeError:
                print(f"Data not found for company ID: {registNo}")
        else:
            print(f"Failed to retrieve data for company ID: {registNo}")
    
    # DataFrame 생성 및 출력
    df = pd.DataFrame(company_data)
    print(df.head())
    df.to_csv("company_data.csv", index=False)  # CSV 파일로 저장
    
    
    
    
