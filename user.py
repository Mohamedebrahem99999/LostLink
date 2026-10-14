from user_repository import UserRepository
from validation import *
# =================================================================
# =======================  Base Class: Account  ======================
# =================================================================
class Account:

    def __init__(
        self,
        user_id,
        email,
        password,
        role = "Member",
        name="undefined",
        phone = "",
        age = 0,
        gender = "",
    ):
      self._user_id = user_id
      self.set_name(name)
      self.set_email(email)
      self.set_password(password)
      self.set_phone(phone)
      self.set_age(age)
      self.set_gender(gender)
      self.set_role(role)
    
    def get_user_id(self):
        return self._user_id
    
    def get_password(self):
        return self._password

    def set_password(self, password):
        self._password = password

    def get_phone(self):
        return self._phone

    def set_phone(self, phone):
      self._phone = phone

    def get_age(self):
        return self._age

    def set_age(self, age):
        self._age = age

    def get_gender(self):
        return self._gender

    def set_gender(self, gender):
        self._gender = gender

    def set_role(self,role):
        self._role = role

    def get_role(self):
        return self._role
    
    def set_name(self,name):
      self._name = name

    def get_name(self):
      return self._name

    def set_email(self,email):
      self._email = email
    
    def get_email(self):
      return self._email

    def display_profile(self):
      return (
          f"ID: {self._user_id} | Name: {self._name} | Email: {self._email} | "
          f"Phone: {self._phone} | Age: {self._age} | Gender: {self._gender} | "
          f"Role: {self._role}"
      )

    @staticmethod
    def add_user():
      print("\n___ Add New User ___")
      
      email = Validation.get_email()
      password = Validation.get_password()
      name = input("Enter Name [default: undefined]: ").strip() or "undefined"
      phone = Validation.get_phone()
      age = Validation.get_age()
      gender = Validation.get_gender()

      user_data = {
          "email": email,
          "password": password,
          "role": "Member",
          "name": name,
          "phone": phone,
          "age": age,
          "gender": gender,
          "borrowed_items": []
      }
      
      UserRepository.add_entry(user_data)