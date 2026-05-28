import pandas as pd


def introduction():
    print(f"Welcome to Farm Sage: Connecting Farmers and Buyers Across Ghana.\n")


def username():
    while True:
        try:
            name = input("What is your name? ").split()
            first_name = name[0]
            last_name = " ".join(name[1:])
            print(f"Welcome, {name[0]}.\n")
            return first_name, last_name
        except Exception:
            print("\nPlease type your name.\n")
            continue


def user_role():
    roles = ["Farmer", "Buyer"]
    print("\nWhat role do you play? \n")

    while True:
        for index, type_of_role in enumerate(roles, start=1):
            print(f"{index}:{type_of_role}")
        try:
            role = input("\nResponse: ")
            role = int(role)
            if not (1 <= role <= len(roles)):
                print("\nPlease enter a valid response.\n")
                continue
            else:
                choice = roles[role-1]
                print(f"\nInput received: {choice}")
                return choice
        except ValueError:
            print("\nInvalid input. Please enter a corresponding number. (1 or 2)\n")


def phone_number():
    country_code = "233"
    while True:
        try:
            phone_number = input(
                "\nStarting with 0XX, enter your phone number: ")
            if len(phone_number) == 10 and phone_number.startswith(str(0)):
                phone_number = phone_number.lstrip(str(0))
                phone_number = country_code + phone_number
                phone_number = int(phone_number)
                print(f"\nPhone number received: {phone_number}.\n")
                return phone_number
            else:
                print("\nPlease enter a 10-digit phone number.\n")
                continue
        except ValueError:
            print("\nInvalid input. Please enter a valid phone number.\n")


def build_dataframe():
    introduction()
    first_name, last_name = username()
    dictionary = {
        "first name": first_name,
        "last name": last_name,
        "choice": user_role(),
        "phone number": phone_number()
    }

    df = pd.DataFrame(dictionary, index=[0])
    df.to_csv('farmer_data.csv')
    print('Loading dashboard...')
    return df


build_dataframe()
