
############### 대한건설업 ##################

import requests
from bs4 import BeautifulSoup
import pandas as pd
import import_ipynb
from date_time import get_first_and_last_day_of_previous_month
import warnings


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
download_file(download_link)

df = pd.read_excel(download_file(download_link))[4:]
new_columns = ['순위', '상호', '대표자', '소재지', '전화번호', '등록번호', '시공능력평가액(토건)', '공사실적평가', '경영평가액', '기술능력평가액', '신인도평가액', '평가액(토목)', '평가액(건축)', '직전년도토건', '직전년도토목', '직전년도건축', '보유기술자수']
df.columns = new_columns
df.insert(0, 'GB', '011')
df.to_csv(f'{Directory}/011_KOR_Cons_{formatted_date}.csv', index=False, sep=',')
