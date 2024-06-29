
from datetime import datetime, timedelta

def get_first_and_last_day_of_previous_month():
    # 현재 날짜
    today = datetime.today()
    
    # 이번 달의 첫 날 계산
    first_day_of_current_month = today.replace(day=1)
    
    # 전월 마지막 날 계산
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    
    # 전월 첫째 날 계산
    first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
    
    return first_day_of_previous_month, last_day_of_previous_month
