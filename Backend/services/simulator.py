import requests, time, random, datetime
from mimesis import Generic

gen = Generic('en')
API = 'http://localhost:5000/api/analyze'

PLATFORMS = ['telegram', 'whatsapp', 'instagram']
def generate_message(user_id):
    text = gen.text.sentence()
    if random.random() < 0.05:
        text += " buy pills 💊 meet asap"
    return {
        "platform": random.choice(PLATFORMS),
        "user_id": f"user_{user_id}",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "text": text
    }

def run_stream(users=20, interval=0.2):
    while True:
        uid = random.randint(0, users-1)
        msg = generate_message(uid)
        try:
            requests.post(API, json=msg, timeout=2)
        except Exception as e:
            print("Post failed:", e)
        time.sleep(interval)

if __name__ == "__main__":
    run_stream()