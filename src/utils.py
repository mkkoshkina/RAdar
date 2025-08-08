from datetime import datetime

def log_message(msg, log_file=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {msg}"
    print(log_msg)
    if log_file:
        with open(log_file, 'a') as f:
            f.write(log_msg + '\n')
            
            