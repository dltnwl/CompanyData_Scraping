
############### 이노비즈 ##################

from datetime import datetime, timedelta
import requests
import pandas as pd
import import_ipynb
from date_time import get_first_and_last_day_of_previous_month
import warnings


warnings.filterwarnings('ignore')

first_day_of_previous_month,  last_day_of_previous_month= get_first_and_last_day_of_previous_month()
formatted_date = first_day_of_previous_month.strftime('%Y%m')


# ASP 파일에서 생성된 HTML 페이지 URL
url = "https://www.innobiz.net/company/new_excel.asp"
params = {
    'startdate': first_day_of_previous_month.strftime('%Y-%m-%d'),
    'enddate': last_day_of_previous_month.strftime('%Y-%m-%d')
}

# GET 요청 보내기
response = requests.get(url, params=params)
if response.status_code == 200:

    # HTML에서 테이블 읽기
    df_list = pd.read_html(response.text)
    if df_list:
        df = df_list[0]  # 첫 번째 테이블 선택

        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)
        
        df.insert(0, 'GB', '002')
        df.drop(columns=['번호'])

        # 쉼표로 구분된 텍스트 파일로 저장
        df.to_csv(f'002_Innobiz_{formatted_date}.csv', index=False, sep=',')
        print("CSV 파일로 변환 완료")
else:
    print("요청 실패:", response.status_code)


