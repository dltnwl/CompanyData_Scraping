############### 정보통신관리협회 ##################

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

    return df

i=1
result_df_f=[]
url='https://ictis.kica.or.kr/construct/compList'
while fetch_data(url, i).columns[0]!='list':
    result_df = fetch_data(url, i)
    result_df_f.append(result_df)
    i=i+1
    
df=pd.concat(result_df_f)
df['id']=df['id'].str.replace('}', '')
df.insert(0, 'GB', '013')
df.to_csv(f'{Directory}/013_Info_Cons_{formatted_date}.csv', index=False)
