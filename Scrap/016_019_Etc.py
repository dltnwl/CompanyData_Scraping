############### 대한기계설비건설협회 ##################
#https://www.kmcca.or.kr/ks/construct/disclosureList.do?goMenuNo=9000000029&topMenuNo=&upperMenuNo=6000000000&pageIndex=3&searchUpjong=27

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import import_ipynb
from date_time import get_first_and_last_day_of_previous_month
import warnings
warnings.filterwarnings('ignore')

first_day_of_previous_month,  last_day_of_previous_month= get_first_and_last_day_of_previous_month()
formatted_date = first_day_of_previous_month.strftime('%Y%m')

year=first_day_of_previous_month.year
month=first_day_of_previous_month.month

Directory='Data'

#12: '기계설비공사', 27: '가스시설공사', 51: '기계설비성능점검업', 73:'기계설비가스공사업'
group_list={12: '016', 27: '017', 51: '018', 73:'019'}


def fetch_data(url):
    response = requests.get(url, verify=False, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 데이터 추출 로직을 구현하세요.
    # 예시: 테이블 데이터 추출
    tables = soup.find_all('table', {'class': 'notice02'})
    if tables:
        headers = [th.text.strip() for th in tables[0].find_all('th')]
        data = []
        for row in tables[0].find_all('tr')[1:]:  # Skipping the header row
            columns = [col.text.strip() for col in row.find_all('td')]
            data.append(columns)
        
        df = pd.DataFrame(data, columns=headers)
        return df

    
all_data_frames = []
for k in group_list:
    i = 1  # 페이지 인덱스 초기화
    while True:  # 무한 루프, 종료 조건을 내부에서 처리
        try:
            url = f'https://www.kmcca.or.kr/ks/construct/disclosureList.do?goMenuNo=9000000029&topMenuNo=&upperMenuNo=6000000000&pageIndex={i}&searchUpjong={k}'
            result_df = fetch_data(url)
            if result_df is None or result_df.empty:
                break  # 데이터가 없거나 fetch_data가 None을 반환하면 루프 종료

            result_df.insert(0, 'GB', group_list[k])
            result_df2 = result_df.drop(columns=['번호'])
            all_data_frames.append(result_df2)
            i += 1  # 페이지 인덱스 증가

        except Exception as e:
            print(f"Error fetching data from {url}: {e}")
            break  # 오류 발생 시 while 루프 종료

        
# Concatenate all DataFrame objects in the list
final_df = pd.concat(all_data_frames, ignore_index=True)

# CSV 파일로 저장
final_df.to_csv(f'{Directory}/016_019_Etc_{formatted_date}.csv', index=False, encoding='euc-kr')
