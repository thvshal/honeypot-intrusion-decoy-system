import socket
import csv
from datetime import datetime
from google import genai

# 1. PASTE YOUR GEMINI API KEY HERE
API_KEY = "YOUR_GEMINI_API_KEY_HERE"

# Initialize Gemini Client
client = genai.Client(api_key=API_KEY)

HOST = '0.0.0.0'  # Localhost
PORT = 2222         # Port listening for connections

LOG_FILE = "attack_logs.csv"

# Initialize CSV log file with headers if it doesn't exist
try:
    with open(LOG_FILE, 'x', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Attacker_IP", "Command", "AI_Response"])
except FileExistsError:
    pass

def get_ai_response(command):
    """Uses Gemini to dynamically simulate a vulnerable Linux server terminal online."""
    prompt = f"""
    You are simulating a vulnerable Linux server terminal for a cybersecurity honeypot.
    The user entered the command: '{command}'
    
    Respond EXACTLY like a real Linux terminal would. 
    If they type 'ls', show realistic fake files (e.g., secret_passwords.txt, db_backup.sql).
    If they try to read a file (e.g., 'cat secret_passwords.txt'), generate fake realistic dummy data.
    Do NOT break character. Keep responses brief and strictly formatted as plain terminal text.
    Do not wrap output in markdown code blocks.
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        return f"bash: {command}: command not found"

def log_attack(ip, command, response):
    """Logs the intrusion activity to CSV."""
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ip, command, response])

def start_honeypot():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Online AI Honeypot Active & Listening on Port {PORT}...")

    while True:
        conn, addr = server.accept()
        print(f"[!] Intrusion Detected from: {addr[0]}")
        conn.sendall(b"Welcome to Ubuntu 22.04 LTS (GNU/Linux 5.15.0 x86_64)\r\nadmin@server:~$ ")
        
        buffer = ""  # Buffer to store incoming keystrokes until Enter is pressed
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                
                # Append received chunks to buffer
                buffer += data.decode('utf-8', errors='ignore')
                
                # Only process when a newline (\n or \r) is received
                if '\n' in buffer or '\r' in buffer:
                    command = buffer.strip()
                    buffer = ""  # Clear buffer for next command
                    
                    if not command:
                        conn.sendall(b"admin@server:~$ ")
                        continue
                    
                    print(f"Attacker Executed: {command}")
                    
                    # Fetch dynamic response from Gemini AI
                    ai_output = get_ai_response(command)
                    log_attack(addr[0], command, ai_output)
                    
                    # Send response back to connection prompt
                    send_data = f"\r\n{ai_output}\r\nadmin@server:~$ "
                    conn.sendall(send_data.encode('utf-8'))
            except ConnectionResetError:
                break
        conn.close()

if __name__ == "__main__":
    start_honeypot()