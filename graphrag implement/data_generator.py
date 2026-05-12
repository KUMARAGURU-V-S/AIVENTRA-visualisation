import os
import pandas as pd
from datetime import datetime, timedelta

def generate_data():
    os.makedirs("source_data", exist_ok=True)
    
    # 1. Chat Logs (Alice and Bob)
    chats = [
        {"timestamp": "2026-05-01 10:00:00", "sender": "Alice", "receiver": "Bob", "message": "Did you get the access credentials for the Charlie's database?"},
        {"timestamp": "2026-05-01 10:05:00", "sender": "Bob", "receiver": "Alice", "message": "Working on it. Sent him the link. Just waiting for the click."},
        {"timestamp": "2026-05-02 14:00:00", "sender": "Bob", "receiver": "Alice", "message": "I'm in. Using IP 192.168.50.122. Downloading the records now."},
        {"timestamp": "2026-05-02 15:30:00", "sender": "Alice", "receiver": "Bob", "message": "Good. Transfer the commission to my offshore account once the buyer pays."},
        {"timestamp": "2026-05-03 09:00:00", "sender": "Bob", "receiver": "Alice", "message": "Payment received. Sending 50,000 to your account ACC-8822."},
    ]
    with open("source_data/chats.txt", "w") as f:
        for chat in chats:
            f.write(f"[{chat['timestamp']}] {chat['sender']} -> {chat['receiver']}: {chat['message']}\n")

    # 2. Server Logs (Charlie's Server)
    server_logs = [
        {"timestamp": "2026-05-02 13:55:00", "event": "LOGIN_SUCCESS", "user": "admin", "ip_address": "192.168.50.122"},
        {"timestamp": "2026-05-02 14:10:00", "event": "DATA_EXPORT", "user": "admin", "ip_address": "192.168.50.122", "details": "Customer_Database_Dump.sql"},
        {"timestamp": "2026-05-02 14:45:00", "event": "LOGOUT", "user": "admin", "ip_address": "192.168.50.122"},
    ]
    pd.DataFrame(server_logs).to_csv("source_data/server_logs.csv", index=False)

    # 3. Bank Records
    bank_records = [
        {"date": "2026-05-03", "from_account": "ACC-5511 (Bob)", "to_account": "ACC-8822 (Alice)", "amount": 50000, "description": "Consultancy Fee"},
        {"date": "2026-05-04", "from_account": "ACC-8822 (Alice)", "to_account": "ACC-9900 (Luxury Jewelers)", "amount": 12000, "description": "Purchase"},
    ]
    pd.DataFrame(bank_records).to_csv("source_data/bank_records.csv", index=False)

    # 4. Emails
    emails = """
From: tech-support@trustworthy.com (Bob)
To: charlie@victim.com
Subject: Urgent: Security Update Required
Date: 2026-05-01 10:15:00

Dear Charlie,
We noticed unusual activity on your account. Please click the link below to verify your identity:
http://malicious-link.com/verify?user=charlie

Regards,
Tech Support
    """
    with open("source_data/emails.txt", "w") as f:
        f.write(emails.strip())

    print("Forensic data generated in ./source_data")

if __name__ == "__main__":
    generate_data()
