import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# 업종별 코드 매핑
group_list = {12: '016', 27: '017', 73: '019'}

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
                    
                    ability_amt = detail_soup.find('th', text='2024 시공능력').parent
                    ability_amt_list = [td.get_text(strip=True) for td in ability_amt.find_all('td')]
                    
                    eval_amt = detail_soup.find('th', text='공사실적평가액').parent
                    eval_amt_list = [td.get_text(strip=True) for td in eval_amt.find_all('td')]
                    
                    business_amt = detail_soup.find('th', text='경영평가액').parent
                    business_amt_list = [td.get_text(strip=True) for td in business_amt.find_all('td')]
                    
                    tech_amt = detail_soup.find('th', text='기술능력평가액').parent
                    tech_amt_list = [td.get_text(strip=True) for td in tech_amt.find_all('td')]
                    
                    new_amt = detail_soup.find('th', text='신인도평가액').parent
                    new_amt_list = [td.get_text(strip=True) for td in new_amt.find_all('td')]
                    
                    old_amt = detail_soup.find('th', text='2023 공사실적').parent
                    old_amt_list = [td.get_text(strip=True) for td in old_amt.find_all('td')]

                    
                    # 상세 정보 추출
                    company_info = {
                        "상호": detail_soup.find("th", text="상호").find_next_sibling("td").text.strip(),
                        "대표자": detail_soup.find("th", text="대표자").find_next_sibling("td").text.strip(),
                        "주소": detail_soup.find("th", text="주소").find_next_sibling("td").text.strip(),
                        "전화번호": detail_soup.find("th", text="전화번호").find_next_sibling("td").text.strip(),
                        "FAX": detail_soup.find("th", text="FAX").find_next_sibling("td").text.strip(),

                        "시공능력 기계설비가스공사업": ability_amt_list[0],
                        "시공능력 [주력분야]기계설비공사": ability_amt_list[1],
                        "시공능력 [주력분야]가스시설공사(제1종)": ability_amt_list[2],
                        "시공능력 주요공종(자동제어)": ability_amt_list[3],
                            
                        "공사실적평가액 기계설비가스공사업": eval_amt_list[0],
                        "공사실적평가액 [주력분야]기계설비공사": eval_amt_list[1],
                        "공사실적평가액 [주력분야]가스시설공사(제1종)": eval_amt_list[2],
                        "공사실적평가액 주요공종(자동제어)": eval_amt_list[3],
                        
                        "경영평가액 기계설비가스공사업": business_amt_list[0],
                        "경영평가액 [주력분야]기계설비공사": business_amt_list[1],
                        "경영평가액 [주력분야]가스시설공사(제1종)": business_amt_list[2],
                        "경영평가액 주요공종(자동제어)": business_amt_list[3],
                        
                        "기술능력평가액 기계설비가스공사업": tech_amt_list[0],
                        "기술능력평가액 [주력분야]기계설비공사": tech_amt_list[1],
                        "기술능력평가액 [주력분야]가스시설공사(제1종)": tech_amt_list[2],
                        "기술능력평가액 주요공종(자동제어)": tech_amt_list[3],
                        
                        "신인도평가액 기계설비가스공사업": new_amt_list[0],
                        "신인도평가액 [주력분야]기계설비공사": new_amt_list[1],
                        "신인도평가액 [주력분야]가스시설공사(제1종)": new_amt_list[2],
                        "신인도평가액 주요공종(자동제어)": new_amt_list[3],
                        
                        "전년도공사실적 기계설비가스공사업": old_amt_list[0],
                        "전년도공사실적 [주력분야]기계설비공사": old_amt_list[1],
                        "전년도공사실적 [주력분야]가스시설공사(제1종)": old_amt_list[2],
                        "전년도공사실적 주요공종(자동제어)": old_amt_list[3],

                        "보유기술자총수":detail_soup.find("th", text="보유기술자총수").find_next_sibling("td").text.strip()
                        }
                    company_details.append(company_info)  # 리스트에 회원 정보 추가
                    
                except AttributeError:
                    print(f"Error retrieving details for memberNo {member_no}, skipping to next.")
        i += 1  # 다음 페이지로 이동
    print(f"업종 {k} 완료.")
    # 데이터프레임 생성 및 CSV로 저장
    final_df = pd.DataFrame(company_details)
    final_df.to_csv(f'016_019_Etc_{formatted_date}_{k}_detail.csv', index=False, encoding='euc-kr')
