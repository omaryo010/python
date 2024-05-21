import json
from firebase_app import firebase_app

# Function to load data from the JSON file
def load_data():
    with open('database.json', 'r') as file :
        data = json.load(file)
    return data 

# Function to save data to the JSON file
def save_data(data):
    with open("database.json", "w") as file:
        json.dump(data, file, indent=4)

# Function to create a new user
def create_product(product_name, price ,qnt,info,img=None):
    data = load_data()
    new_product = {
        "product_name": product_name,
        "price": price,
        "qnt":qnt,
        "info":info,
        "img":img
    }

    data["products"].append(new_product)
    save_data(data)
    firebase_app.write_data("/products/",new_product)

# Function to get all users
def get_all_product():
    data = load_data()
    return data["products"]

# Function to find a user by username
def find_product(product_name):
    data = load_data()
    for product in data["products"]:
        if product["product_name"] == product_name:
            return product
    return None

# Function to update a user's email
def update_product_price(product_name, new_price ,new_qnt):
    data = load_data()
    for product in data["products"]:
        if product["product_name"] == product_name:
            product["price"] = new_price
            product["qnt"] == new_qnt
            save_data(data)
            return True
    return False

# Function to delete a user
def delete_product(product_name):
    data = load_data()
    for product in data["products"]:
        if product["product_name"] == product_name:
            data["products"].remove(product)
            save_data(data)
            return True
    return False

#function print users
def print_products():
    print("All products:")
    for product in get_all_product():
        print(product)
    data = firebase_app.read_data("/products/")
    for key in data :
        print(key , firebase_app.read_data(f'/products/{key}'))

#function find user
def find_products(product_name):
    print(f"\nFind {product_name}:")
    product = find_product(product_name)
    if product:
        print(product)
    else:
        print("product not found")
        ################
    data = firebase_app.read_data('/products/')
    for p in data :
        object = firebase_app.read_data(f'/products/{p}')
        if object['product_name'] == product_name:
            print('we fount the object !!!!')
            print(p,object)
        else:
            print('no product')
#function update 
def update(product,price):
    print("\nUpdate product price:")
    if update_product_price(product, price):
        print("price updated")
    else:
        print("product not found")
#function delete
def delete_products(product):
    print("\nDelete product:")
    if delete_product(product):
        print(f"{product} deleted")
    else:
        print(f"{product} not found")
    data = firebase_app.read_data('/products/')
    for p in data :
        object = firebase_app.read_data(f'/products/{p}')
        if object['product_name'] == product:
            print('we fount the object !!!!')
            firebase_app.delet_data(f'/products/{p}')

