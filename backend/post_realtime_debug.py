import requests
url='http://127.0.0.1:8000/api/run_pipeline_realtime'
print('Posting to',url)
try:
    r=requests.post(url,json={'run_id':'rt_debug','metrics':{'accuracy':0.7}}, timeout=15)
    print('Status',r.status_code)
    print('Text repr:', repr(r.text[:2000]))
except Exception as e:
    print('Error:',e)
