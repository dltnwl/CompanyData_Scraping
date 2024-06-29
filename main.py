import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

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
filename = '001_NewTech_202405.csv'
filepath = filename  # 파일 경로 설정

# MIMEBase 객체 생성
attachment = open(filepath, "rb")  # 파일을 바이너리 형식으로 읽기

part = MIMEBase('application', 'octet-stream')
part.set_payload(attachment.read())  # 파일 내용을 MIMEBase 객체에 추가
encoders.encode_base64(part)  # Base64 인코딩 수행

part.add_header(
    'Content-Disposition',
    f'attachment; filename= {filename}',
)

msg.attach(part)  # 완성된 파트(첨부 파일)를 메시지 객체에 추가

# 메일 보내기
smtp.sendmail('dltnwl93@gmail.com', 'dltnwl9322@gmail.com', message.as_string())

print("성공적으로 메일을 보냈습니다.")

# 파일 닫기
attachment.close()

# 세션 종료
smtp.quit()
