import smtplib
from email.message import EmailMessage
def send(data,img):
    # Email content
    email = EmailMessage()
    email['From'] = 'omaryo010pop@gmail.com'  # Replace with your Gmail address
    email['To'] = 'omaryo020pop@gmail.com'  # Replace with recipient's email
    email['Subject'] = 'طلب منتج '
    

    # Gmail SMTP configuration
    gmail_user = 'omaryo010pop@gmail.com'  # Replace with your Gmail address
    gmail_password = 'eflv meno jqnj xjla'  # Replace with your Gmail password
    try:
        #with open(img, 'rb') as file:
        #    image_data = file.read()
        #    image_name = 'image.jpg'  # Change the filename as needed
        email.set_content(data)
        #email.add_attachment(image_data, maintype='image', subtype='jpeg', filename=image_name)
    except Exception as e :
        error= str(e)
        email.set_content(data+error)

    try:
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        
        # Send the email
        server.send_message(email)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
    finally:
        # Close the connection
        server.quit()

