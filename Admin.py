from datetime import date, timedelta
import re
from user import Account

# =================================================================
# ====================  Subclass 2: Manager  ======================
# =================================================================
class Admin(Account):

  def __init__(
      self,
      manager_id,
      name,
      email,
      password,
      phone="",
      age=0,
      gender="",
  ):
    
    super().__init__(
        user_id=manager_id,
        name=name,
        email=email,
        password=password,
        phone=phone,
        age=age,
        gender=gender,
        role = "Manager"
    )
    self.__manager_id = manager_id
    self._role = "Manager"

  def set_manager_id(self, manager_id):
    self.__manager_id = manager_id
  def display_profile(self):
    base_info = super().display_profile()
    return f"{base_info}"