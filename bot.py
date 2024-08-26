import pickle
from collections import UserDict
from datetime import datetime

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        self.validate(value)
        super().__init__(value)

    def validate(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits.")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_to_remove = self.find_phone(phone)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)

    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit:
            self.remove_phone(old_phone)
            self.add_phone(new_phone)
        else:
            raise ValueError(f"Phone number {old_phone} not found.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def add_birthday(self, value):
            self.birthday = Birthday(value)

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        birthday = f", Birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, Phones: {phones}{birthday}"

class AddressBook(UserDict):
    
    def add_record(self, record):
        self.data[record.name.value] = record
    
    def find(self, name):
        return self.data.get(name, None)
    
    def delete(self, name):
        if name in self.data:
            self.data.pop(name)

    def string_to_date(self, date_string):
        return datetime.strptime(date_string, "%Y.%m.%d").date()

    def date_to_string(self, date):
        return date.strftime("%Y.%m.%d")

    def prepare_user_list(self):
        prepared_list = []
        for record in self.data.values():
            prepared_list.append({"name": record.name, "birthday": self.string_to_date(record.birthday)})
        return prepared_list

    def find_next_weekday(self, start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date.replace(day=start_date.day + days_ahead)

    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0)
        return birthday

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = datetime.today().date()

        for record in self.data.values():
            if not record.birthday:
                continue
            birthday = datetime.strptime(record.birthday.value, '%d.%m.%Y').date()
            birthday_this_year = birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            birthday_this_year = self.adjust_for_weekend(birthday_this_year)

            if 0 <= (birthday_this_year - today).days <= days:
                congratulation_date_str = self.date_to_string(birthday_this_year)
                upcoming_birthdays.append({"name": record.name.value, "congratulation_date": congratulation_date_str})

        return upcoming_birthdays
    
    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())
    
class Birthday(Field):
    def __init__(self, value):  
        super().__init__(value)
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Enter the argument for the command"
        except KeyError:
            return "Name is not in the list of contacts"
        except IndexError:
            return "Input correct arguments please"

    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, contacts: AddressBook):
    name, phone, *_ = args
    record = contacts.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        contacts.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, contacts: AddressBook):
    name, old_phone, new_phone = args
    record = contacts.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact change."
    else:
        return "Name was not found"

@input_error    
def show_phone(args, contacts):
    name, = args
    record = contacts.find(name)
    if record:
        return record
    else: 
        return "Name was not found"
    
@input_error
def add_birthday(args, contacts):
    name, day = args
    record = contacts.find(name)
    if record:
        record.add_birthday(day)
        return "Birthday added"
    else:
        "Name was not found"

@input_error
def show_birthday(args, contacts):
    name, = args
    record = contacts.find(name)
    if record and record.birthday:
        return f"Birthday for {name}: {record.birthday}"
    else:
        return "Birthday not found."

@input_error
def birthdays(contacts, days=7):
    return contacts.get_upcoming_birthdays(days)
 
def all(contacts):
    return contacts


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()
    

def main():
    contacts = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, contacts))
        elif command == "change":
            print(change_contact(args, contacts))
        elif command == "phone":
            print(show_phone(args, contacts))
        elif command == "all":
            print(all(contacts))
        elif command == "add-birthday":
            print(add_birthday(args, contacts))
        elif command == "show-birthday":
            print(show_birthday(args, contacts))
        elif command == "birthdays":
            print(birthdays(contacts))
        else:
            print("Invalid command.")

    save_data(contacts)

if __name__ == "__main__":
    main()

