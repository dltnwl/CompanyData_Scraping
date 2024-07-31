############### 소방시설협회 ##################
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import math
import import_ipynb
from date_time import get_first_and_last_day_of_previous_month
import warnings
warnings.filterwarnings('ignore')

first_day_of_previous_month,  last_day_of_previous_month= get_first_and_last_day_of_previous_month()
formatted_date = first_day_of_previous_month.strftime('%Y%m')

year=first_day_of_previous_month.year
month=first_day_of_previous_month.month


def fetch_data(url):
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 데이터 추출 로직을 구현하세요.
    # 예시: 테이블 데이터 추출
    tt=soup.find_all('div', {'class': 'table-list'})
    headers = [th.text.strip() for th in tt[1].find_all('th')]
    data = []
    for no, row in enumerate(tt[1].find_all('tr')):
        if no==0:
            pass
        else:
            columns = [col.text.strip() for col in row.find_all('td')]
            data.append(columns)

    df = pd.DataFrame(data, columns=headers)
    return df

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
response = requests.get('https://ftis.ekffa.or.kr/fe/construct/NR_listRanking.do?currentPage=1&year=2023&searchType=1000', headers=headers, verify=False, timeout=5)


soup = BeautifulSoup(response.text, 'html.parser')
count_div = soup.find('p', class_='board-count')
number_of_companies = re.findall(r'[^\uAC00-\uD7A3]+',count_div.span.text)
cleaned_s = number_of_companies[0].replace(',', '').strip()

# 문자열을 정수로 변환
number = int(cleaned_s)
end_page=math.ceil(int(number)/10)


result_df_f=[]
for i in range(1,end_page+1):
    url=f'https://ftis.ekffa.or.kr/fe/construct/NR_listRanking.do?currentPage={i}&year=2023&searchType=1000'
    result_df = fetch_data(url)
    result_df_f.append(result_df)

df=pd.concat(result_df_f)
df.insert(0, 'GB', '015')
df.to_csv(f'015_Fire_{formatted_date}.csv', index=False, encoding='euc-kr')
print(df)
