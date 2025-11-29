import requests, json
url='http://127.0.0.1:8000/api/run_pipeline'
data={'run_id':'test_post_1','metrics':{'accuracy':0.9}}
print('Posting to',url)
try:
    r=requests.post(url,json=data,timeout=30)
    print('Status',r.status_code)
    try:
        print('JSON:',json.dumps(r.json(),indent=2)[:2000])
    except Exception as e:
        print('Text:', r.text[:2000])
except Exception as e:
    print('Error:',e)
