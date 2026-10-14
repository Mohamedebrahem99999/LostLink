import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from constants import *
from my_lib import *
from validation import Validation
from user_repository import UserRepository

class ResetPassword:
    def __init__(self,receiver_email):
        self.receiver_email = receiver_email
        self.rand_code = generate_rand_code(100000,999999)
    
    def write_email(self):
        """
        sends a code to the user's email
        """
        message = MIMEMultipart()
        message["From"] = SENDEREMAIL
        message["To"] = self.receiver_email
        message["Subject"] = "Forgetten Passwod"
        body = f"""Dear Customer,
        
            We received a request to reset the password for your SIC Smart Bank account.
    
            Your verification code is:
            {self.rand_code}
            Please do not share this code with anyone for security reasons.
    
            If you did not request a password reset, please ignore this email.
    
            Best regards,
            SIC Smart Bank Support Team"""
        message.attach(MIMEText(body, "plain", "utf-8"))
        return message

    def send_email(self):
        message = self.write_email()
        server = None
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()  
            server.login(SENDEREMAIL, PASSWORD)
            server.sendmail(SENDEREMAIL, self.receiver_email, message.as_string())
            print("A code was sent successfully to ",self.receiver_email)
            return True
        except Exception as e:
            print(f"Error while sending {e}")
            return False
    
        finally: # بس كدا مش هيخش على finally
            if server:
                server.quit()

    def reset_password(self,id):
        """
        allows the user to update his password
        """
        new_password = Validation.get_password()
        UserRepository.update_data(id,"password",new_password)

    def verify_email(self,id):
        self.send_email()
        while True:
            user_code = input("Eneter the verification code: ")
            
            print("Verifying...")
            time.sleep(1)
            if check_equality(str(self.rand_code),user_code):
                print("email Verified✅✅")
                self.reset_password(id)
                return True
            else:
                print("wrong entered code")
                print("""
                    1.Resend code again
                    2.Retry to enter the code
                    or enter anything else to return to enter password page
                    """)
                user_choice = input()
                if user_choice == "1":
                    self.rand_code = generate_rand_code(100000,999999)
                    self.send_email()
                elif user_choice == "2":
                    continue
                else:
                    print("Reset password process cancelled.")
                    return False