
############### 대한건설업 ##################

import requests
from bs4 import BeautifulSoup
import pandas as pd
import import_ipynb
from date_time import get_first_and_last_day_of_previous_month
import warnings
import re

warnings.filterwarnings('ignore')

first_day_of_previous_month,  last_day_of_previous_month= get_first_and_last_day_of_previous_month()
formatted_date = first_day_of_previous_month.strftime('%Y%m')

year=first_day_of_previous_month.year
month=first_day_of_previous_month.month

# 웹 페이지 URL 설정
url = 'http://www.cak.or.kr/board/boardList.do?boardId=news_notice&menuId=101'  # 예시 URL

# 웹 페이지에서 HTML 가져오기
response = requests.get(url)
html = response.text

# BeautifulSoup 객체 생성
soup = BeautifulSoup(html, 'html.parser')

# 모든 링크(<a> 태그)를 찾음
links = soup.find_all('a')

Directory='Data'

# 특정 텍스트를 포함하는 링크 찾기
for link in links:
    if link.text and  f"{Directory}/{year}년도 종합건설사업자 시공능력평가액 공시" in link.text.strip():
        print("찾은 링크:", link)
        break

# 연결된 다운로드 링크 찾기
download_link = soup.find('a', href=lambda href: href and "fileDownload.do" in href and "dataId=39614" in href)
if download_link:
    full_download_url = f"http://www.cak.or.kr{download_link['href']}"
    print("다운로드 링크:", full_download_url)

def download_file(url):
    # URL에서 파일 ID 추출하여 파일 이름 설정
    file_id = url.split('dataId=')[1].split('&')[0]  # URL에서 dataId 값 추출
    local_filename = f"{Directory}/downloaded_file_{file_id}.xlsx"  # 예: downloaded_file_39614.pdf

    # 파일 다운로드
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

# 다운로드 링크 설정 (실제 URL로 대체 필요)
download_link = 'http://www.cak.or.kr/board/ajax/fileDownload.do?dataId=39614&boardId=news_notice'

# 파일 다운로드 실행
local_filename = download_file(download_link)

# 엑셀 파일의 각 시트를 읽어옴
excel_file = pd.ExcelFile(local_filename)
sheet_names = excel_file.sheet_names

# 각 시트를 DataFrame으로 변환하여 하나의 DataFrame으로 결합
all_data = pd.DataFrame()
for sheet in sheet_names:
    if sheet=='1. 토건': 
        df = pd.read_excel(excel_file, sheet_name=sheet, skiprows=4)
        new_columns = ['순위', '상호', '대표자', '소재지', '전화번호', '등록번호', '시공능력평가액(토건)', 
                       '공사실적평가', '경영평가액', '기술능력평가액', '신인도평가액', '평가액(토목)', '평가액(건축)', 
                       '직전년도토건', '직전년도토목', '직전년도건축', '보유기술자수']
        df.columns = new_columns
        df.insert(0,'전체건수', df['순위'].max())  # 전체 건수 추가 
        
        # '직전년도토건', '직전년도토목', '직전년도건축' 및 '시공능력평가액(토건)', '평가액(토목)', '평가액(건축)'을 각각 변환하여 행으로 결합
        df_togon = df[['전체건수', '순위',  '상호', '대표자', '소재지', '전화번호', '등록번호', '공사실적평가', 
                       '경영평가액', '기술능력평가액', '신인도평가액', '보유기술자수']].copy()
        df_togon['업종'] = '토건'
        df_togon['주력분야'] = np.nan
        df_togon['시공능력평가액'] = df['시공능력평가액(토건)']
        df_togon['직전년도평가액'] = df['직전년도토건']
        
        df_tomok = df[['전체건수', '순위', '상호', '대표자', '소재지', '전화번호', '등록번호', '공사실적평가', 
                       '경영평가액', '기술능력평가액', '신인도평가액', '보유기술자수']].copy()
        df_tomok['업종'] = '토건(토목)'
        df_tomok['주력분야'] = np.nan
        df_tomok['시공능력평가액'] = df['평가액(토목)']
        df_tomok['직전년도평가액'] = df['직전년도토목']
        
        df_geonchuk = df[['전체건수', '순위', '상호', '대표자', '소재지', '전화번호', '등록번호', '공사실적평가', 
                          '경영평가액', '기술능력평가액', '신인도평가액', '보유기술자수']].copy()
        df_geonchuk['업종'] = '토건(건축)'
        df_geonchuk['주력분야'] = np.nan
        df_geonchuk['시공능력평가액'] = df['평가액(건축)']
        df_geonchuk['직전년도평가액'] = df['직전년도건축']
        
        all_data = pd.concat([df_togon, df_tomok, df_geonchuk], ignore_index=True)

        columns_order = ['업종', '주력분야', '전체건수', '순위', '상호', '대표자', '소재지', '전화번호', '등록번호', '시공능력평가액', '공사실적평가', 
                         '경영평가액', '기술능력평가액', '신인도평가액', '직전년도평가액', '보유기술자수']
        all_data = all_data[columns_order]
    
    else:
        df = pd.read_excel(excel_file, sheet_name=sheet, skiprows=4)
        new_columns = ['순위', '상호', '대표자', '소재지', '전화번호', '등록번호', '시공능력평가액', '공사실적평가', 
                       '경영평가액', '기술능력평가액', '신인도평가액', '직전년도평가액', '보유기술자수']
        df.columns = new_columns
        df.insert(0,'업종', re.findall(r'[가-힣]+',sheet)[0])  # 시트 이름을 새로운 열로 추가
        df.insert(1,'주력분야', np.nan)  # 전체 건수 추가 
        df.insert(2,'전체건수', df['순위'].max())  # 전체 건수 추가 
        
        all_data = pd.concat([all_data, df], ignore_index=True)


int_columns = ['전체건수','순위', '등록번호',  '시공능력평가액', '공사실적평가', '경영평가액', '기술능력평가액', 
               '신인도평가액', '직전년도평가액', '보유기술자수']
for col in int_columns:
    all_data[col] = pd.to_numeric(all_data[col], errors='coerce').fillna(0).astype(int)

# GB 열 추가
all_data.insert(0, 'GB', '종합')


# 결합된 데이터를 하나의 CSV 파일로 저장
all_data.to_csv(f'{Directory}/011_KOR_Cons_{formatted_date}.csv', index=False, sep=',')

print("모든 시트가 결합되어 하나의 CSV 파일로 저장되었습니다.")
