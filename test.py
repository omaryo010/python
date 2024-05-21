
from flask import Flask, render_template , jsonify
from threading import Thread
from flask import request as r
from data.firebase_app import firebase_app
import json
from scrap_html.app import search as p 
from scrap_html.pross import pross_data
from scrap_html.counter import most_common_value ,closest_to_most_common

app = Flask(__name__)
def get_data():
    products1 = firebase_app.read_data("/products/")
    products =[]
    for p in products1 :
        products.append(products1[p])

    return products

def thread(arg):
    ps =Thread(target=arg)
    ps.start()
    
@app.route('/')
def index():
    products = get_data()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product(product_id):
    products = get_data()
    if 1 <= product_id <= len(products):
        #print(products[product_id])
        return render_template('product.html', product=products[product_id - 1],id=product_id)   
    else:
        return "Product not found", 404
    
@app.route('/request/<int:id>')
def request(id):
    products = get_data()
    if 1 <= id <= len(products):
        return render_template('request.html',product=products[id-1],id=id)

@app.route('/process/<int:id>', methods=['POST'])
def process(id):
    products = get_data()
    name = str(r.form['name'])
    phone_number= str(r.form['phone'])
    addrs= str(r.form['addrs'])
    wilaya = str(r.form['wilaya'])
    product=(products[id-1])
    imgs = product['img']
    img =''
    for i in imgs :
        img = img +'\n'+ i
    print(img)
    data = name + '\n'+phone_number+'\n' + addrs + '\n'+ wilaya +'\n'+ img
    import send_gmail
    send_gmail.send(data=data,img=img)
    return render_template('confermation.html',name=name,phone=phone_number,addrs=addrs,wilaya=wilaya)

@app.route('/search', methods=['GET'])
def search():
    sample_data = {}
    i = 0 
    for n in get_data() :
        sample_data[n['product_name']] = i
        i= i+ 1 
    query = r.args.get('query', '').lower()
    suggestions = {}
    for item in sample_data :
        if query in item.lower():
            suggestions[sample_data[item]+1] = item

    return jsonify(dict(list(suggestions.items())[:5]))  # Return up to 5 suggestions

@app.route('/search/get')
def search_get():
    query = int(r.args.get('query', '').lower())
    products = get_data()
    if 1 <= query <= len(products):
        return jsonify(products[query-1])
    
@app.route('/pross_data',methods=['GET','POST'])
def pross_data():
    results = None
    query = ""
    if r.method == 'POST':
        query = r.form['query']
        results=p.search(query)
        data = []
        labels = []
        for result in results:
            data.append(int(results[result][1]))
            labels.append(results[result][0])
        closest_value = closest_to_most_common(data)
        return render_template('pross_data.html', results=results, query=query,prix=data,names=labels)
    if r.method == 'GET':
        data = None
        labels = None
        return render_template('pross_data.html',prix=data,names=labels)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80,debug=True)
