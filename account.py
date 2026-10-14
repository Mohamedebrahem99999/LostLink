class Account:
    def __init__(self, user_id, name, email, password, phone="", age=0, gender="", role="Member"):
        self._user_id = str(user_id)
        self._name = name
        self._email = email
        self._password = password
        self._phone = phone
        self._age = age
        self._gender = gender
        self._role = role

    def get_user_id(self):
        return self._user_id

    def get_name(self):
        return self._name

    def get_email(self):
        return self._email

    def get_role(self):
        return self._role

    def display_profile(self):
        return (
            f"ID: {self._user_id} | "
            f"Name: {self._name} | "
            f"Email: {self._email} | "
            f"Phone: {self._phone or 'N/A'} | "
            f"Age: {self._age or 'N/A'} | "
            f"Gender: {self._gender or 'N/A'} | "
            f"Role: {self._role}"
        )