import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def notify_parent(alert_type: str, content: str, result: dict):
    """
    Gửi thông báo cho phụ huynh qua email và in ra console.
    """
    print(f"[ALERT to Parents] Type={alert_type} | Content={content} | Result={result}")

    try:
        with open("config.json") as f:
            config = json.load(f)["email"]

        # --- Tạo nội dung email ---
        subject = f"Cảnh báo an toàn cho trẻ: Phát hiện {alert_type}"
        body = f"""
        Chào quý phụ huynh,

        Hệ thống giám sát AI vừa phát hiện một hoạt động có khả năng không an toàn.

        - **Loại cảnh báo:** {alert_type}
        - **Nội dung:** {content}
        - **Kết quả phân tích:**
            - Nhãn: {result['label']}
            - Độ tin cậy: {result['score']:.2f}

        Vui lòng kiểm tra và trao đổi với con em mình.

        Trân trọng,
        Hệ thống AI Child Protection
        """

        # --- Gửi email ---
        msg = MIMEMultipart()
        msg['From'] = config["sender_email"]
        msg['To'] = config["recipient_email"]
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
        server.starttls()
        server.login(config["sender_email"], config["sender_password"])
        text = msg.as_string()
        server.sendmail(config["sender_email"], config["recipient_email"], text)
        server.quit()

        print(f"[EMAIL] Alert sent to {config['recipient_email']}")

    except FileNotFoundError:
        print("[ERROR] config.json not found. Skipping email notification.")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
