import json

def pross_data():
    result = {}
    with open('data.json','r') as data :
        data=json.load(data)
        b=0
        results =''
        for i in data :
            product = data[f"{i}"]
            if product[5] != 'None':
                if product[5] != '10000':
                    results = results +'name:'+product[0]+"<br>price: "+ product[5]+'<br>'
                    result[f'product{b}']=[product[0],product[5]]
                    print(result)
                    b=b+1
        #result = json.dumps(result)
        #with open('result.json','w') as r :
        #    r.write(result)
        #print(results)
    return result