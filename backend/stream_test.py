import requests, time, sys
url='http://127.0.0.1:8000/api/run_pipeline_realtime'
print('Posting to', url)
try:
    r = requests.post(url, json={'run_id':'test123','metrics':{'accuracy':0.9}}, stream=True, timeout=20)
    print('Status code:', r.status_code)
    if r.status_code!=200:
        print('Response text:', r.text[:1000])
    else:
        it = r.iter_lines()
        start=time.time()
        count=0
        for line in it:
            if line:
                try:
                    print('LINE:', line.decode('utf-8'))
                except:
                    print('LINE (raw):', line)
                count+=1
            if count>=6 or time.time()-start>12:
                break
        r.close()
except Exception as e:
    print('POST error:', e)
    sys.exit(1)
print('done')
