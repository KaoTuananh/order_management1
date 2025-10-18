class Customer:
    def __init__(self, customer_id, name, address, phone, contact_person):

        self.__customer_id = customer_id
        self.__name = name
        self.__address = address
        self.__phone = phone
        self.__contact_person = contact_person

    # Геттеры (Методы для чтения приватных данных)
    def get_customer_id(self):
        return self.__customer_id

    def get_name(self):
        return self.__name

    def get_address(self):
        return self.__address

    def get_phone(self):
        return self.__phone

    def get_contact_person(self):
        return self.__contact_person

    # Сеттеры (Методы для изменения приватных данных)
    def set_customer_id(self, customer_id):
        self.__customer_id = customer_id

    def set_name(self, name):
        self.__name = name

    def set_address(self, address):
        self.__address = address

    def set_phone(self, phone):
        self.__phone = phone

    def set_contact_person(self, contact_person):
        self.__contact_person = contact_person