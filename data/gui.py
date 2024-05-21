import procc_data
import os 
import tkinter as tk
from tkinter import filedialog
import shutil
from time import sleep
from firebase_app import firebase_app

def select_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    file_path = filedialog.askopenfilename()  # Open file dialog
    if file_path:
        print("Selected file:", file_path)
        # You can use file_path variable to access the selected file's path
        file_name = os.path.basename(file_path)
        data = {"name": file_name, "path": file_path}
        return data
    
def copy_file(source_path, destination_path):
    try:
        shutil.copy2(source_path, destination_path)
        print(f"File copied from '{source_path}' to '{destination_path}' successfully.")
    except FileNotFoundError:
        print("File not found or unable to copy.")

while True:
    print('\n hello to data base products\n')
    print('1 - Create New product ')
    print('2 - Delete product')
    print('3 - find product')
    print('4 - show list products')
    print('5 - update product and price')
    cmd = input('$ ')
    if cmd =='1':
        product_name = input('enter the name of product: ')
        price = input('enter ther pricel: ')
        qnt = input('enter the quantity:  ')
        info=input("write info about your product: ")
        c = input('do you have image for your product !! ')
        procc_data.create_product(product_name,price,qnt,info)
        if c == 'y':
            try:
                data = select_file()
                database = firebase_app.read_data('/products/')
                for p in database :
                    object = firebase_app.read_data(f'/products/{p}')
                    if object['product_name'] == product_name and object['price']== price and object['qnt']== qnt:
                        print('we fount the object !!!!')
                        firebase_app.upload_images(data['path'],p+"/"+data['name'])
                img_path = firebase_app.get_path_images(p+'/'+data['name'])
                copy_file(data['path'] , f'/home/kali/Desktop/python/python/static/img/{data["name"]}')
                img = img_path
                firebase_app.update_data('/products/'+ p +'/'+'img',img)
            except Exception as e :
                print(e)
                firebase_app.delet_data('/product'+p)
        os.system('clear')


    elif cmd == '2':
        product_name= input('enter the product name that you wont to delete !: ')
        cnf =input(f'are you sur to delete {product_name}? (y or n ) : ')
        if cnf == 'y':
            procc_data.delete_products(product_name)
        else :
            print(product_name , "not deleted")
        sleep(5)
        os.system('clear')

    elif cmd == '3':
        product_name = input('enter name product to serch for : ')
        os.system('clear')
        procc_data.find_products(product_name)
    
    elif cmd == '4':
        procc_data.print_products()
    
    elif cmd == '5' :
        product_name = input('enter the name of product that you wont to update : ')
        price = input('enter the new price : ')
        qnt = input('enter the quantity : ')
        os.system('clear')
        procc_data.update_product_price(product_name,price,qnt)



        


        






#procc_data.create_product('kit','200','4')
#procc_data.delete_product("kit")
procc_data.find_products('kit')
procc_data.print_products()
procc_data.update_product_price('kit','400')


