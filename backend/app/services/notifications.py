import requests

def send_webhook(url, payload):
    if not url: return {"sent":False,"reason":"WEBHOOK_URL not configured"}
    try:
        r=requests.post(url,json=payload,timeout=10); r.raise_for_status(); return {"sent":True,"status":r.status_code}
    except Exception as e: return {"sent":False,"error":str(e)}
