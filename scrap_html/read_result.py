import json

try:
    with open('result.json','r') as f:
        data=json.load(f)
        print(data) 
        for i in data :
            for i in data[i]:
                print(i)
except Exception as e :
    print(e)
