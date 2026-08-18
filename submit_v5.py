# -*- coding: utf-8 -*-
import json, os, sys, time, requests

BASE = "https://paperreview.ai"
PDF = "/data/vergil-CCF/ccf/04_论文写作/论文_v5/paper.pdf"
EMAIL = "3514056593@qq.com"
VENUE = "ICLR"
OUT = "/data/vergil-CCF/ccf/05_评测与迭代/提交记录_token_v5.txt"

s = requests.Session()

# 1. get presigned url
r = s.post(BASE + "/api/get-upload-url", json={"filename": os.path.basename(PDF), "venue": VENUE}, timeout=60)
print("get-upload-url status", r.status_code)
print(r.text[:500])
r.raise_for_status()
data = r.json()
if not data.get("success"):
    raise SystemExit("get-upload-url failed: " + str(data))
presigned_url = data["presigned_url"]
s3_key = data["s3_key"]
fields = data["presigned_fields"]

# 2. upload to S3
with open(PDF, "rb") as f:
    files = {"file": (os.path.basename(PDF), f, "application/pdf")}
    form = fields.copy()
    # requests will add file after fields if we pass data=form and files=files
    r2 = requests.post(presigned_url, data=form, files=files, timeout=300)
print("s3 upload status", r2.status_code)
print(r2.text[:300])
r2.raise_for_status()

# 3. confirm
r3 = s.post(BASE + "/api/confirm-upload", data={"s3_key": s3_key, "venue": VENUE, "email": EMAIL}, timeout=120)
print("confirm status", r3.status_code)
print(r3.text[:1000])
r3.raise_for_status()
res = r3.json()
if not res.get("success"):
    raise SystemExit("confirm failed: " + str(res))

token = res.get("token", "")
message = res.get("message", "")
with open(OUT, "w", encoding="utf-8") as f:
    f.write(f"paper: paper.pdf\nvenue: {VENUE}\nemail: {EMAIL}\ntime: {time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())}\ntoken: {token}\nmessage: {message}\n")
print("saved", OUT)
print("TOKEN", token)
