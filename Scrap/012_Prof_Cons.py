import requests
import pdfplumber
import zipfile
import os
import pandas as pd
from urllib.parse import quote
import import_ipynb
from date_time import get_first_and_last_day_of_previous_month
import warnings
import re
warnings.filterwarnings('ignore')

def get_first_and_last_day_of_previous_month():
    from datetime import datetime, timedelta
    today = datetime.today()
    first = today.replace(day=1) - timedelta(days=1)
    last = first.replace(day=1)
    return last, first

# 날짜 정보 가져오기
first_day_of_previous_month, last_day_of_previous_month = get_first_and_last_day_of_previous_month()
year = first_day_of_previous_month.strftime('%Y')
formatted_date = first_day_of_previous_month.strftime('%Y%m')

Directory = 'Data'
os.makedirs(Directory, exist_ok=True)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
})

file_name = f'전문건설업시공능력평가공시({year})_주력분야.xlsx'
encoded_file_name = quote(file_name.encode('euc-kr'))
file_url = f'https://kosca.or.kr/public/down_kosca/NewFdown.asp?FN={encoded_file_name}&idx=3589&TB=KOSCA_GONGJI&FP=notice/{year}-07/&area=00'

response = session.get(file_url, allow_redirects=True, verify=False)

if response.status_code == 200:
    local_path = f'{Directory}/{file_name}'
    with open(local_path, 'wb') as f:
        f.write(response.content)
    print("File downloaded successfully!")
    
    # 엑셀 파일의 각 시트를 읽어옴
    excel_file = pd.ExcelFile(local_path)
    sheet_names = excel_file.sheet_names

    # 각 시트를 DataFrame으로 변환하여 하나의 DataFrame으로 결합
    all_data = pd.DataFrame()
    for sheet in sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet, skiprows=2)
        new_columns = ['No', '상호', '대표자', '소재지', '전화번호',  '시공능력평가액', 
                       '공사실적평가', '경영평가액', '기술능력평가액', '신인도평가액', '직전년도평가액', '보유기술자수', '비고']
        df.columns = new_columns
        df['업종'] = re.findall(r'[가-힣]+', sheet)[0]
        df['주력분야'] = np.nan  
        df['등록번호'] = np.nan  
        df['순위'] = df.groupby('업종').apply(lambda x: x.sort_values(by=['시공능력평가액', '직전년도평가액'], ascending=[False, False])) \
                        .reset_index(level=0, drop=True).groupby('업종').cumcount() + 1
        df['전체건수'] = df['순위'].max()
        df['평가액(토목)'] = np.nan
        df['평가액(건축)'] = np.nan
        df['직전년도토목'] = np.nan
        df['직전년도건축'] = np.nan        
        all_data = pd.concat([all_data, df], ignore_index=True)
    
    # GB 열 추가
    all_data.insert(0, 'GB', '전문')

    columns_order = ['GB', '업종', '주력분야', '순위',  '전체건수','상호', '대표자', '소재지', '전화번호', '등록번호', 
                     '시공능력평가액', '공사실적평가', '경영평가액', '기술능력평가액', '신인도평가액', '직전년도평가액', '보유기술자수']
    all_data = all_data[columns_order]

    # 결합된 데이터를 하나의 CSV 파일로 저장
    all_data.to_csv(f'{Directory}/012_Prof_Cons_{formatted_date}.csv', index=False, sep=',', encoding='euc-kr')
else:
    print("Failed to download the file. Status code:", response.status_code)

