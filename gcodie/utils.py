from datetime import datetime
import os

def stats(text):
    ctime = datetime.now().strftime("%H:%M:%S")
    print(f"[Status  -  {ctime}] Gcodie✿  {text}")

# Clear the screen
def tidy():

    global no_stats

    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception as e:
        stats(f"Error while clearing the screen: {e}")
    stats("Screen cleared")