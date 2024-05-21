
import firebase_admin
import json
from firebase_admin import credentials,initialize_app,db,storage

cred = credentials.Certificate("data/firebase_app/auth.json")
#firebase_admin.initialize_app(cred)
app =initialize_app(cred,{
    "databaseURL":"https://website-87954-default-rtdb.firebaseio.com/","storageBucket":"website-87954.appspot.com"
})
def get_path_images(name):
    bucket = storage.bucket()
    print(name)
    path = bucket.get_blob(f'images/{name}').path
    path = f"https://firebasestorage.googleapis.com/v0{path}?alt=media&token=dcd1376c-7948-4313-9c01-97a54debd12f"
    print(path)
    return path

def upload_images(path,name):
    bucket = storage.bucket()
    blob = bucket.blob(f'images/{name}')
    blob.upload_from_filename(path)

def write_data(path,data):
    ref = db.reference(path)
    ref.push(data)
    print('database has created')

def read_data(path):
    ref =db.reference(path)
    return ref.get()

def update_data(path,data):
    ref=db.reference(path)
    ref.set(data)

def delet_data(path):
    ref= db.reference(path)
    ref.set({})

#write_data('/stok',"data.json")
#print(read_data("/stoke/"))
#update_data('/stoke/products/product1/name',"wail")
#delet_data("stoke/products/product1")
#get_path_images()
#read_data("/")