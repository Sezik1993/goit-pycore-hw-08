from collections import UserDict


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


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []

    def add_phone(self, phone):
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)

    def edit_phone(self, old_phone, new_phone):
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

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Where is the name and phone, bro?"
        except KeyError:
            return "I`m blind or i can`t find it"
        except IndexError:
            return "Enter the argument for the command"

    return inner


@input_error
def add_contact(args, contacts):
    name, phone = args
    name = name.lower()
    contacts[name] = phone
    return "Contact added."


@input_error
def change_contact(args, contacts):
    name, phone = args
    name = name.lower()
    if name in contacts:
        contacts[name] = phone
        return "Contact updated, bro!"
    else:
        raise KeyError()


@input_error
def show_all(contacts):
    if not contacts:
        return "There are no contacts yet."
    result = ""
    for name, phone in contacts.items():
        result += f"{name.title()}: {phone}\n"
    return result.strip()


@input_error
def show_phone(args, contacts):
    name = args[0].lower()
    if name in contacts:
        return f"{name.title()}: {contacts[name]}"
    else:
        raise KeyError()


def show_help():
    return (
        "Available commands:\n"
        "  hello                   - Greet the bot\n"
        "  add <name> <phone>      - Add a new contact\n"
        "  change <name> <phone>   - Change the phone number for an existing contact\n"
        "  phone <name>            - Show the phone number of a contact\n"
        "  show all                - Show all contacts\n"
        "  help                    - Show this help message\n"
        "  close / exit            - Exit the assistant"
    )


def main():
    print("Welcome to the super duper terminal bot")
    contacts = {}

    while True:
        user_input = input("Enter command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("See you later!!!")
            break

        elif command == "hello":
            print("What can I do for you, bro?")

        elif command == "add":
            print(add_contact(args, contacts))

        elif command == "change":
            print(change_contact(args, contacts))

        elif command == "phone":
            print(show_phone(args, contacts))

        elif command == "show":
            if args and args[0].lower() == "all":
                print(show_all(contacts))
            else:
                print("To see all contacts, type: show all")

        elif command == "help":
            print(show_help())
        else:
            print("something wrong.")


if __name__ == "__main__":
    main()


# # Testing classes
# if __name__ == "__main__":
#     # Create a new address book
#     book = AddressBook()
#
#     # Create a record for John
#     john_record = Record("John")
#     john_record.add_phone("1234567890")
#     john_record.add_phone("5555555555")
#
#     # Add John record to an address book
#     book.add_record(john_record)
#
#     # Create and add a new record for Jane
#     jane_record = Record("Jane")
#     jane_record.add_phone("9876543210")
#     book.add_record(jane_record)
#
#     # Display all records in the book
#     print("All contacts:")
#     for name, record in book.data.items():
#         print(f"{name}: {[phone.value for phone in record.phones]}")
#
#     # Find a specific record
#     john = book.find("John")
#     print(f"\nJohn's phones: {[phone.value for phone in john.phones]}")
#
#     # Edit phone number
#     john.edit_phone("1234567890", "1112223333")
#     print(f"John's phones after editing: {[phone.value for phone in john.phones]}")
#
#     # Remove phone number
#     john.remove_phone("5555555555")
#     print(f"John's phones after removal: {[phone.value for phone in john.phones]}")
#
#     # Delete record
#     book.delete("Jane")
#     print(f"\nContacts after deleting Jane: {list(book.data.keys())}")