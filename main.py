import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# 스크래핑 수행하기 
import subprocess
from Scrap.date_time import get_first_and_last_day_of_previous_month

# Scrap 폴더 안의 스크립트 실행 목록
scripts = [
    '001_NewTech.py',
    '002_InnoBiz.py',
    '003_Mainbiz.py',
    '004_CompanyLab.py'
]

# 각 스크립트를 subprocess로 실행
for script in scripts:
    script_path = f"Scrap/{script}"  # 스크립트 경로
    print(f"Running {script_path}...")  # 실행 중인 스크립트 출력
    result = subprocess.run(['python', script_path], capture_output=True, text=True)

    # 실행 결과 출력
    if result.returncode == 0:
        print("Output:")
        print(result.stdout)  # 스크립트 실행 결과 출력
    else:
        print("Error:")
        print(result.stderr)  # 에러 메시지 출력

print("All scripts executed.")


############메일보내기#################
# SMTP 인스턴스 생성
smtp = smtplib.SMTP('smtp.gmail.com', 587)

# TLS 보안 시작
smtp.starttls()

# 서버 로그인
smtp.login('dltnwl93@gmail.com', 'dmhl xrxd ahvw iswh')

# MIMEMultipart 객체 생성
msg = MIMEMultipart()

# 메일 내용
msg['Subject'] = '제목: 파일 첨부 테스트'
body = '본문: Hello, this is a test email with attachment.'
msg.attach(MIMEText(body, 'plain'))

# 첨부 파일 경로

filenames = [f'001_NewTech_{formatted_date}.csv', 
             f'002_Innobiz_{formatted_date}.csv', 
             f'003_Mainbiz_{formatted_date}.csv', 
             f'004_Company_lab_{formatted_date}.csv'
            ]
folder_path = 'Scrap/'  # 파일이 위치한 폴더 경로

# 파일 첨부 과정
for filename in filenames:
    filepath = f"{folder_path}{filename}"
    attachment = open(filepath, "rb")  # 파일을 바이너리 형식으로 읽기

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)  # Base64 인코딩 수행

    part.add_header(
        'Content-Disposition',
        f'attachment; filename="{filename}"'
    )
    msg.attach(part)  # 메시지 객체에 파일 첨부
    attachment.close()  # 파일 닫기


# 메일 보내기
smtp.sendmail('dltnwl93@gmail.com', 'dltnwl9322@gmail.com', msg.as_string())

print("성공적으로 메일을 보냈습니다.")

# 파일 닫기
attachment.close()

# 세션 종료
smtp.quit()
