############### 기업부설연구소 현황 ##################

import requests
import import_ipynb
import pandas as pd
from date_time import get_first_and_last_day_of_previous_month
import warnings


warnings.filterwarnings('ignore')

first_day_of_previous_month,  last_day_of_previous_month= get_first_and_last_day_of_previous_month()
formatted_date = first_day_of_previous_month.strftime('%Y%m')


# URL 설정
download_url = "https://www.rnd.or.kr/user/infoservice/search5.do"

# 다운로드 요청에 필요한 데이터 설정
payload = {
    'currentPage': '1',
    'excel_yn': 'Y'
}

# 세션 시작
session = requests.Session()

# POST 요청 보내기
response = session.post(download_url, data=payload)

Directory='Data'

# 응답 확인 및 파일 저장
if response.status_code == 200:
    with open('{Directory}/companylab_download.xlsx', 'wb') as file:
        file.write(response.content)

    df = pd.read_excel('{Directory}/companylab_download.xlsx')
    
    df.insert(0, 'GB', '004')
    #df2=df.drop(columns=['Unnamed: 0'])
    df.to_csv(f'{Directory}/004_Company_lab_{formatted_date}.csv', index=False, sep=',')
    
    print("엑셀 파일 다운로드 완료")
else:
    print("요청 실패:", response.status_code)
