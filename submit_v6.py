# -*- coding: utf-8 -*-
import json, os, sys, time, requests

BASE = "https://paperreview.ai"
PDF = "/data/vergil-CCF/ccf/04_论文写作/论文_v6/paper.pdf"
EMAIL = "3514056593@qq.com"
VENUE = "ICLR"
OUT = "/data/vergil-CCF/ccf/04_论文写作/论文_v6/提交记录_token_v6.txt"

s = requests.Session()
r = s.post(BASE + "/api/get-upload-url", json={"filename": os.path.basename(PDF), "venue": VENUE}, timeout=60)
print("get-upload-url", r.status_code)
r.raise_for_status()
data = r.json()
if not data.get("success"):
    raise SystemExit("get-upload-url failed: " + str(data))
presigned_url = data["presigned_url"]
s3_key = data["s3_key"]
fields = data["presigned_fields"]

with open(PDF, "rb") as f:
    files = {"file": (os.path.basename(PDF), f, "application/pdf")}
    r2 = requests.post(presigned_url, data=fields.copy(), files=files, timeout=300)
print("s3 upload", r2.status_code)
r2.raise_for_status()

r3 = s.post(BASE + "/api/confirm-upload", data={"s3_key": s3_key, "venue": VENUE, "email": EMAIL}, timeout=120)
print("confirm", r3.status_code)
print(r3.text[:1000])
r3.raise_for_status()
res = r3.json()
if not res.get("success"):
    raise SystemExit("confirm failed: " + str(res))

token = res.get("token", "")
message = res.get("message", "")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(f"paper: paper.pdf\nvenue: {VENUE}\nemail: {EMAIL}\ntime: {time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())}\ntoken: {token}\nmessage: {message}\n")
print("saved", OUT)
print("TOKEN", token)
