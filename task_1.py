import pickle
from collections import UserDict
from datetime import datetime, timedelta

""" базовий клас Field для обробки загальних функцій полів """
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

""" клас Name успадковує Field, представляє ім'я контакту """
class Name(Field):
    pass

""" клас Phone успадковує Field, представляє номер телефону контакту """
class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Invalid phone number. Must contain exactly 10 digits")
        super().__init__(value)

""" клас Birthday успадковує Field і представляє день народження """
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

""" клас Record для обробки інформації про окремий контакт """
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))
        
    def remove_phone(self, phone_value):
        self.phones = [phone for phone in self.phones if phone.value != phone_value]
        
    def edit_phone(self, old_phone_value, new_phone_value):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone_value:
                self.phones[i] = Phone(new_phone_value)
                return
        raise ValueError("Phone number not found")    
        
    def find_phone(self, phone_value):
        for phone in self.phones:
            if phone.value == phone_value:
                return phone
        return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {', '.join(p.value for p in self.phones)}"
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

""" клас AddressBook успадковує UserDict, є колекцією записів """
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Record not found")
        
    def get_upcoming_birthdays(self, days=7):
        today = datetime.today().date()
        upcoming_birthdays = []
    
        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year).date()

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                
                days_left = (birthday_this_year - today).days
                if 0 <= days_left <= days:
                    if birthday_this_year.weekday() in (5, 6):
                        birthday_this_year += timedelta(days=(7 - birthday_this_year.weekday()))
                
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": birthday_this_year.strftime("%d-%m-%Y")
                    }) 
            
        return upcoming_birthdays


# Функція для збереження адресної книги у файл
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)
        print("Address book saved to disk.")

# Функція для завантаження адресної книги з файлу
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            book = pickle.load(f)
            print("Address book loaded from disk.")
            return book
    except FileNotFoundError:
        print("No saved address book found, starting with a new one.")
        return AddressBook()


def main():
    # Завантаження адресної книги при запуску
    book = load_data()

    while True:
        command = input("Enter a command (add, find, delete, quit): ").strip().lower()
        
        if command == "add":
            name = input("Enter contact name: ")
            phone = input("Enter contact phone: ")
            record = Record(name)
            record.add_phone(phone)
            book.add_record(record)
            print(f"Added contact: {name} with phone: {phone}")
        
        elif command == "find":
            name = input("Enter contact name to find: ")
            record = book.find(name)
            if record:
                print(f"Found: {record}")
            else:
                print("Record not found.")

        elif command == "delete":
            name = input("Enter contact name to delete: ")
            try:
                book.delete(name)
                print(f"Deleted contact: {name}")
            except ValueError as e:
                print(e)

        elif command == "quit":
            # Збереження адресної книги перед виходом
            save_data(book)
            print("Exiting the program.")
            break
        else:
            print("Invalid command, please try again.")


if __name__ == "__main__":
    main()