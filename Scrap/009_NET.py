############### NET ##################

import requests
from bs4 import BeautifulSoup
import pandas as pd
import pdfplumber
import import_ipynb
from date_time import get_first_and_last_day_of_previous_month
import warnings

warnings.filterwarnings('ignore')

first_day_of_previous_month,  last_day_of_previous_month= get_first_and_last_day_of_previous_month()
formatted_date = first_day_of_previous_month.strftime('%Y%m')

year=first_day_of_previous_month.year
month=first_day_of_previous_month.month

# 파일 다운로드 URL 설정
base_url = 'https://www.netmark.or.kr/bbs_download.asp?'
params = {
    'sCate': 'notice',
    'idx': '434',
    'fnum': '1'
}

if month==5: 
    No=1
elif month==9:
    No=2
elif month==1:
    No=3

# 파일 다운로드 요청
response = requests.get(base_url, params=params)

Directory='Data'

# 요청 성공 여부 확인
if response.status_code == 200:
    with open(f'{Directory}/{year}년 제{No}회 신기술(NET) 인증기술 공고.pdf', 'wb') as f:
        f.write(response.content)
    print("Download completed successfully!")
else:
    print("Failed to download the file.")
    

# PDF 파일 열기
with pdfplumber.open(f'{Directory}/{year}년 제{No}회 신기술(NET) 인증기술 공고.pdf') as pdf:
    # 추출한 데이터프레임을 저장할 리스트
    all_tables = []
    
    # 각 페이지를 순회하면서 테이블 추출
    for page in pdf.pages:
        # 페이지에서 테이블 추출
        tables = page.extract_tables()
        
        # 각 테이블을 판다스 데이터프레임으로 변환
        for table in tables:
            df = pd.DataFrame(table[1:], columns=table[0])
            all_tables.append(df)
    
    # 결과 출력 (첫 번째 테이블만 출력)
    if all_tables:
        df2=all_tables[0].drop(columns=['인증\n번호'])
        df3 = df2.replace('\n', ' ', regex=True)
        df3.insert(0, 'GB', '009')
        df4 = df3.rename(columns={'유효\n기간': '유효기간'})
        df4.to_csv(f'{Directory}/009_NET_{formatted_date}.csv', index=False, sep=',')
    else:
        print("No tables found in the PDF.")
