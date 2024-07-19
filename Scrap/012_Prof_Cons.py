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

# 날짜 정보 가져오기
first_day_of_previous_month, last_day_of_previous_pi = get_first_and_last_day_of_previous_month()
formatted_date = first_day_of_previous_month.strftime('%Y%m')

Directory='Data'

session = requests.Session()  # 세션 시작
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
})

# 필요한 경우 로그인 등의 초기 세팅을 수행하여 쿠키를 획득
# login_response = session.post("https://example.com/login", data={"username": "user", "password": "pass"})

file_name = '전문건설업시공능력평가공시(2023)주력분야.zip'  # 예를 들어 파일 이름이 한글일 경우
encoded_file_name = quote(file_name.encode('euc-kr'))  # 한국에서 많이 사용하는 euc-kr 인코딩을 가정
file_url = f'https://kosca.or.kr/public/down_kosca/NewFdown.asp?FN={encoded_file_name}&idx=3437&TB=KOSCA_GONGJI&FP=notice/2023-07/&area=00'

response = session.get(file_url, allow_redirects=True)

if response.status_code == 200:
    with open(f'{Directory}/전문건설업시공능력평가공시(2023)주력분야.zip', 'wb') as f:
        f.write(response.content)
    print("ZIP file downloaded successfully!")
else:
    print("Failed to download the file. Status code:", response.status_code)
    

# PDF 파일 열기
zip_path = f'{Directory}/전문건설업시공능력평가공시(2023)주력분야.zip'


# 추출할 디렉토리
extract_dir = f'{Directory}/extracted'
os.makedirs(extract_dir, exist_ok=True)

# ZIP 파일 열기
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    # ZIP 파일 내의 모든 파일을 추출 디렉토리로 추출
    zip_ref.extractall(extract_dir)
    
    full_data=[]
    for file_name in zip_ref.namelist():
        decoded_file_name = file_name.encode('cp437').decode('euc-kr')
        if file_name.endswith('.pdf'):
            # PDF 파일의 전체 경로
            pdf_path = os.path.join(extract_dir, file_name)
            
            # PDF 파일 열기
            with pdfplumber.open(pdf_path) as pdf:
                all_tables = []
                # 각 페이지를 순회하며 텍스트 추출
                for page in pdf.pages:
                    tables = page.extract_tables()
                        # 각 테이블을 판다스 데이터프레임으로 변환
                    for table in tables:
                        nm_list=['연번', '상호', '대표자', '소재지', '전화번호', '시공능력평가액', '공사실적평가액', '경영평가액', '기술능력평가액', '신인도평가액', '직전년도공사실적', '기술자수', '비고']
                        df = pd.DataFrame(table[2:], columns=nm_list)
                        all_tables.append(df)  # 생성된 DataFrame을 리스트에 추가
            
                
                # CSV 파일로 저장
                if all_tables:
                    combined_df = pd.concat(all_tables, ignore_index=True)  # 여러 DataFrame을 하나로 결합
                    combined_df['업종'] =re.search(r'\d+([^\d\(\)]+)\(', decoded_file_name).group(1)
                    combined_df['주력분야'] =re.search(r'\((.*?)\)', decoded_file_name).group(1)
                    combined_df['순위']=combined_df['시공능력평가액'].rank(ascending=False, method='min')
                    combined_df.insert(0,'전체건수', combined_df['연번'].max())  # 전체 건수 추가 
                    # CSV 파일로 저장
                    csv_path = os.path.join(extract_dir, f"012_{os.path.splitext(decoded_file_name)[0]}_{formatted_date}.csv")
                    combined_df.to_csv(csv_path, index=False, encoding='utf-8-sig', sep=',')
        
        full_data.append(combined_df)
    
    full_data_df=pd.concat(full_data)
    full_data_df.insert(0, 'GB', '전문')
    full_data_df.to_csv(f"{Directory}/012_Prof_Cons_{formatted_date}.csv", index=False, encoding='utf-8-sig', sep=',')
