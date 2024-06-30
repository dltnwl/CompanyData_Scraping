import requests
from bs4 import BeautifulSoup
import pandas as pd
import math
import import_ipynb
from date_time import get_first_and_last_day_of_previous_month
import warnings
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
warnings.filterwarnings('ignore')

# 날짜 정보 가져오기
first_day_of_previous_month, last_day_of_previous_pi = get_first_and_last_day_of_previous_month()
formatted_date = first_day_of_previous_month.strftime('%Y%m')

Directory='Data'

# 실패한 페이지 시작 번호를 읽는 함수
def read_failed_line():
    try:
        with open(f'{Directory}/failed_page.txt', 'r') as file:
            line = file.read().strip()
            return int(line) if line.isdigit() else 1  # 숫자인 경우에만 int로 변환
    except FileNotFoundError:
        return 1  # 파일이 없으면 처음부터 시작
    except ValueError:  # 파일 내용이 숫자로 변환할 수 없는 경우
        return 1  # 기본값으로 1을 반환

def write_failed_start(page_number):
    with open(f'{Directory}/failed_page.txt', 'w') as file:
        file.write(str(page_number))

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})
retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# 데이터 추출 함수
def fetch_data(url):

    try:
        response = session.get(url, verify=False, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table', {'class': 'txtC'})
        if tables:
            table = tables[0]
            headers = [th.text.strip() for th in table.find_all('th')]
            data = []
            for row in table.find_all('tr')[1:]:
                columns = [col.text.strip() for col in row.find_all('td')]
                data.append(columns)
            
            processed_data = []
            for i in range(1, len(data), 2):
                if i+1 < len(data):
                    row = data[i] + data[i+1]
                    processed_data.append(row)
            
            headers = ['번호', '지역', '등록번호', '대표자', '상호', '시공능력평가액', '공사실적평가액','경영평가액','기술능력평가액','신인도평가액','전년도공사실적총액']
            df = pd.DataFrame(processed_data, columns=headers)
            return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# 페이지 수 계산 및 데이터 수집
start_page = read_failed_line()
response = requests.get(f'https://www.keca.or.kr/ecic/om/om1004.do?menuCd=5016&currentPageNo={start_page}', verify=False)
soup = BeautifulSoup(response.text, 'html.parser')
count_div = soup.find('div', class_='count')
number_of_companies = count_div.span.text
end_page = math.ceil(int(number_of_companies) / 10)

# n페이지씩 나누어 처리
epoch=2000
for chunk_start in range(start_page, end_page + 1, epoch):
    chunk_end = min(chunk_start + epoch-1, end_page)
    all_data_frames = []
    for i in range(chunk_start, chunk_end + 1):
        url = f'https://www.keca.or.kr/ecic/om/om1004.do?menuCd=5016&currentPageNo={i}'
        df = fetch_data(url)
        if df is not None:
            all_data_frames.append(df)
            success = True
        else:
            write_failed_start(i)
            success = False
            break  # 실패 시 중단하고 실패한 페이지 기록
            
    if not success:
        print(f"Data fetching failed at page {i}, stopping...")
        break  # 외부 for 루프를 종료
    
    # 데이터 결합 및 CSV 파일로 저장
    if all_data_frames:
        final_df = pd.concat(all_data_frames, ignore_index=True)
        final_df.insert(0, 'GB', '014')
        filename = f'{Directory}/014_Elec_{formatted_date}_pages_{chunk_start}_to_{chunk_end}.csv'
        final_df.to_csv(filename, index=False, encoding='utf-8-sig')
