import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# 업종별 코드 매핑
group_list = {12: '016', 27: '017', 51: '018', 73: '019'}

# 회원 정보를 저장할 리스트 초기화
company_details = []

# 각 업종별로 페이지를 순회
for k in group_list:
    i = 1  # 페이지 인덱스 초기화
    while True:  # 페이지 순회
        url = f'https://www.kmcca.or.kr/ks/construct/disclosureList.do?goMenuNo=9000000029&topMenuNo=&upperMenuNo=6000000000&pageIndex={i}&searchUpjong={k}&searchSingoYear=2024'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 페이지에서 회원 링크 추출
        links = soup.find_all('a', {"onclick": re.compile(r"main\('V','(\d+)',''\);")})
        if not links:  # 링크가 없으면 마지막 페이지로 간주
            break
        
        # 각 링크에서 회원 번호 추출 및 상세 정보 수집
        for link in links:
            onclick_attr = link.get('onclick')
            match = re.search(r"main\('V','(\d+)',''\);", onclick_attr)
            if match:
                member_no = match.group(1)
                detail_url = f"https://www.kmcca.or.kr/ks/construct/disclosure.do?memberNo={member_no}&sidohoCode=value&searchSingoYear=2024"
                detail_response = requests.get(detail_url)
                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                
                try:
                    # 상세 정보 추출
                    company_info = {
                        "상호": detail_soup.find("th", text="상호").find_next_sibling("td").text.strip(),
                        "대표자": detail_soup.find("th", text="대표자").find_next_sibling("td").text.strip(),
                        "주소": detail_soup.find("th", text="주소").find_next_sibling("td").text.strip(),
                        "전화번호": detail_soup.find("th", text="전화번호").find_next_sibling("td").text.strip(),
                        "FAX": detail_soup.find("th", text="FAX").find_next_sibling("td").text.strip(),
                        "2024 시공능력": detail_soup.find("th", text="2024 시공능력").find_next_sibling("td").text.strip(),
                        "공사실적평가액": detail_soup.find("th", text="공사실적평가액").find_next_sibling("td").text.strip(),
                        "경영평가액": detail_soup.find("th", text="경영평가액").find_next_sibling("td").text.strip(),
                        "기술능력평가액": detail_soup.find("th", text="기술능력평가액").find_next_sibling("td").text.strip(),
                        "신인도평가액": detail_soup.find("th", text="신인도평가액").find_next_sibling("td").text.strip()
                        }
                    company_details.append(company_info)  # 리스트에 회원 정보 추가
                except AttributeError:
                    print(f"Error retrieving details for memberNo {member_no}, skipping to next.")
        i += 1  # 다음 페이지로 이동

# 데이터프레임 생성 및 CSV로 저장
final_df = pd.DataFrame(company_details)
final_df.to_csv(f'{Directory}/016_019_Etc_{formatted_date}.csv', index=False, encoding='euc-kr')
