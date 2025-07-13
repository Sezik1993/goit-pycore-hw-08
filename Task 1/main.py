from collections import UserDict
from datetime import datetime, timedelta
import pickle


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
        if not self.validate_phone(value):
            raise ValueError("Phone number must be 10 digits")
        super().__init__(value)

    def validate_phone(self, phone):
        return phone.isdigit() and len(phone) == 10


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)

    def edit_phone(self, old_phone, new_phone):
        # Validate old phone format first
        if not (old_phone.isdigit() and len(old_phone) == 10):
            raise ValueError("Old phone number must be 10 digits")

        phone_obj = self.find_phone(old_phone)
        if phone_obj:
            try:
                new_phone_obj = Phone(new_phone)
                index = self.phones.index(phone_obj)
                self.phones[index] = new_phone_obj
            except ValueError as e:
                raise ValueError(f"Invalid new phone format: {e}")
        else:
            raise ValueError("Phone not found")

    def find_phone(self, phone):
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                return phone_obj
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_to_birthday = (birthday_this_year - today).days

                if 0 <= days_to_birthday <= 7:
                    congratulation_date = birthday_this_year

                    if congratulation_date.weekday() == 5:
                        congratulation_date += timedelta(days=2)
                    elif congratulation_date.weekday() == 6:
                        congratulation_date += timedelta(days=1)

                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": congratulation_date.strftime("%d.%m.%Y")
                    })

        return upcoming_birthdays


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Input error: {e}"
        except KeyError:
            return "Contact was not found."
        except IndexError:
            return "Insufficient arguments for the team."

    return inner


@input_error
def add_contact(args, book):
    if len(args) < 2:
        raise IndexError("Name and phone must be provided.")

    name = args[0]
    phone = args[1]

    record = book.find(name)
    message = "Contact has been updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "The contact has been added."

    record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    if len(args) < 3:
        raise IndexError("You need to specify the name, old phone and new phone.")

    name = args[0]
    old_phone = args[1]
    new_phone = args[2]

    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact has been updated."
    else:
        raise KeyError()


@input_error
def show_phone(args, book):
    if len(args) < 1:
        raise IndexError("Name must be specified.")

    name = args[0]
    record = book.find(name)
    if record:
        if record.phones:
            phones = '; '.join(p.value for p in record.phones)
            return f"{name}: {phones}"
        else:
            return f"{name}: No phones"
    else:
        raise KeyError()


@input_error
def show_all(book):
    if not book.data:
        return "There are no contacts yet."
    result = ""
    for record in book.data.values():
        result += f"{record}\n"
    return result.strip()


@input_error
def add_birthday(args, book):
    if len(args) < 2:
        raise IndexError("You must specify the name and date of birth.")

    name = args[0]
    birthday = args[1]

    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday has been added."
    else:
        raise KeyError()


@input_error
def show_birthday(args, book):
    if len(args) < 1:
        raise IndexError("Name must be specified.")

    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday:
            return f"Birthday {name}: {record.birthday}"
        else:
            return f"У {name} no birthday is set"
    else:
        raise KeyError()


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "There are no birthdays in the next week."

    result = "The coming birthday:\n"
    for person in upcoming:
        result += f"{person['name']}: {person['congratulation_date']}\n"
    return result.strip()


def show_help():
    return (
        "Available commands:\n"
        "  hello                   - Greet the bot\n"
        "  add <name> <phone>      - Add a new contact\n"
        "  change <name> <old_phone> <new_phone> - Change the phone number for an existing contact\n"
        "  phone <name>            - Show the phone number of a contact\n"
        "  all                     - Show all contacts\n"
        "  add-birthday <name> <birthday> - Add birthday to contact\n"
        "  show-birthday <name>    - Show birthday of a contact\n"
        "  birthdays               - Show upcoming birthdays\n"
        "  help                    - Show this help message\n"
        "  close / exit            - Exit the assistant"
    )


def main():
    book = load_data()
    print("Welcome to the super duper terminal bot")

    while True:
        user_input = input("Enter command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("See you later, bro!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        elif command == "help":
            print(show_help())

        else:
            print("something wrong.")

    save_data(book)


if __name__ == "__main__":
    main()