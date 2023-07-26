import gspread
from google.oauth2.service_account import Credentials

import random
import string

from datetime import datetime

from pycountry import countries

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('magnolia_airport')


# Flights worksheet in project spreadsheet
FLIGHTS_WS = SHEET.worksheet("flights")

# List of countries, taken from pycountry countries object
# Note that this list is not perfect - includes some subdivisions of countries,
# e.g. individual islands
COUNTRIES = [country.name.upper() for country in countries]


def get_flights_ws_column_no(heading):
    """
    Get the column number of the passed heading in the flights worksheet.
    Column order can be changed or new columns added without breaking the program
    """
    return FLIGHTS_WS.find(heading).col


def readable_passenger_details(passenger):
    """
    Create a string with the details for the passed passenger, printed in a human-readable format
    """
    readable_details = f"{passenger['first name']} {passenger['last name']}"

    # Add line for each detail except first and last name to string
    for key, value in passenger.items():
        if key == "first name" or key == "last name":
            continue
        
        readable_details += (f"\n   {key.capitalize()}: {value}")

    readable_details += f"\n"
    
    return readable_details


def view_all_passenger_details():
    """
    Asks the user for a flight number, then prints a readable output of all
    passengers on that flight and their details
    """
    print("""
----------------------------------------
View Passenger Details
----------------------------------------
    """)
    flight_nos_column = get_flights_ws_column_no("flight no")
    flight_nos = FLIGHTS_WS.col_values(flight_nos_column)

    while True:
        flight = input("Please input a flight number: ")

        try:
            if flight in flight_nos:
                print(f"\n", get_all_passenger_details(flight))
                break
            else:
                raise ValueError("Invalid flight number")
        except ValueError as e:
            print(f"{e}, please try again\n")


def get_all_passenger_details(flight_number):
    """
    View all passengers and their details on the flight with the provided number
    """
    worksheet_to_view = SHEET.worksheet(flight_number)

    # Get passenger info as a list of dictionaries
    passengers = worksheet_to_view.get_all_records()

    passengers_display_string = ""

    for passenger in passengers:
        details = readable_passenger_details(passenger)
        passengers_display_string += f"{details}\n"
    
    return passengers_display_string


def book_ticket():
    """
    Add a new passenger to a flight.
    Will ask for user input to determine which flight they want to book
    and get passenger details.
    """
    print("""
----------------------------------------
Ticket Booking
----------------------------------------
    """)

    # Ask for intended destination and check that there is a flight there
    while True:
        # Get user input for flight destination
        destination = input("What is the destination? ").capitalize()

        # From spreadsheet, pull all flight destinations
        destinations_column = get_flights_ws_column_no("destination")
        destinations_list = FLIGHTS_WS.col_values(destinations_column)[1:]
        destinations_set = set(destinations_list)

        readable_destinations = ", ".join(destinations_set)

        # If the desired destination not available, inform user of this and loop starts again
        # If the destination is available, loop breaks and function continues
        if destination not in destinations_set:
            print(f"""
No flights to {destination}.
Available destinations:

---
{readable_destinations}
---

Please try again.
""")
        else:
            break

    flight_row = FLIGHTS_WS.find(destination).row
    flight_times_column = get_flights_ws_column_no("departure time")
    flight_time = FLIGHTS_WS.cell(flight_row, flight_times_column).value

    # Ask user if the flight at a certain time should be booked
    # If yes, continue booking
    # If no, function stops and code returns to main program
    while True:
        print(f"\nWe have a flight to {destination} at {flight_time} today.")
        continue_booking = input("Is that ok? (yes/no): ")

        if continue_booking.lower() == "yes":
            break
        elif continue_booking.lower() == "no":
            while True:
                new_request = input("Would you like to book a different flight? ")

                if new_request.lower() == "yes":
                    print()
                    book_ticket()
                    # After re-calling function above, first time function call is still running,
                    # and will come back to this loop when the second function call stops.
                    # This return means that when the main function call comes back here,
                    # it will end
                    return
                elif new_request.lower() == "no":
                    print("Goodbye, have a nice day")
                    print(f"Exiting ticket booking...\n")
                    return
                else:
                    print(f"Please type 'yes' or 'no' only\n")
        else:
            print(f"Please type 'yes' or 'no' only\n")
        
    # Ask user questions to get passenger details
    print(f"\nPassenger Details")
    passenger_details = get_passenger_details()

    # Pull flight number from "flights" worksheet
    flight_number = FLIGHTS_WS.cell(flight_row, 1).value

    # Get list of used booking numbers to ensure there is no repetition
    booking_nos_worksheet = SHEET.worksheet("booking nos")
    used_booking_nos = booking_nos_worksheet.col_values(1)

    while True:
        # Generate a sequence of 2 letters, 2 numbers, 2 letters, 2 numbers for a booking reference
        # Example booking no: TF78RE32
        characters_list = []
        for i in range(2):
            characters_list.extend(random.choices(string.ascii_uppercase, k=2))
            characters_list.extend([random.randint(1, 9) for i in range(2)])

        # Join booking number characters into a single string
        booking_no = ""
        for character in characters_list:
            booking_no += (str(character))

        # Check that booking number has not already been used
        # If it has, generate a new one
        if booking_no not in used_booking_nos:
            break
    
    # Add generated booking number for this passenger to worksheet of used numbers
    booking_nos_worksheet.append_row([booking_no])

    # Add booking number to passenger details
    passenger_details.append(booking_no)

    print(f"\nAdding passenger to flight...")

    # Add the passenger details to a new row in the flight's worksheet
    flight_worksheet = SHEET.worksheet(flight_number)
    flight_worksheet.append_row(passenger_details)

    print(f"\nPassenger {passenger_details[0]} {passenger_details[1]} successfully added to flight {flight_number}")

    # Get and format flight date
    flight_dates_column = get_flights_ws_column_no("date")
    flight_date_str = FLIGHTS_WS.cell(flight_row, flight_dates_column).value
    flight_date = datetime.strptime(flight_date_str, '%Y-%m-%d').date()
    formatted_flight_date = flight_date.strftime("%b %-d, %Y")

    # 's' suffix for 0 or 2 luggage pieces
    suffix = "s"
    if passenger_details[5] == 1:
        suffix = ""

    booking_confirmation_message = f"""

----------------------------------------
YOUR BOOKING

Flight no. {flight_number} to {destination} on {formatted_flight_date} at {flight_time}

Name: {passenger_details[0]} {passenger_details[1]}
Booking no: {passenger_details[6]}
Luggage: {passenger_details[5]} piece{suffix}
----------------------------------------

    """

    print(booking_confirmation_message)


def get_passenger_details():
    """
    Gets passenger details and returns them in a list
    """
    passenger_details = []
    details = ["first name", "last name", "date of birth", "passport no", "nationality", "luggage"]

    # Get input for each required detail
    # Run detail through validator function and repeat request until correct data entered,
    # then append to passenger_details list
    for detail in details:
        while True:
            if detail == "date of birth":
                info = input(f"\nPlease enter {detail} (YYYY-MM-DD): ")
            elif detail == "nationality":
                print(f"\nNationality:")
                print("   If input country name doesn't work, please try writing it")
                print("   a different way (e.g. for UK type United Kingdom).")
                info = input(f"\nPlease enter {detail}: ")
            elif detail == "luggage":
                info = input(f"\nHow many items of checked luggage would you like to book? (max. 2) ")
            else:
                info = input(f"\nPlease enter {detail}: ")
            
            validated_info = validate_passenger_detail(detail, info)

            if validated_info["validity"]:
                break
        
        passenger_details.append(validated_info["data"])
        
    return passenger_details


def validate_passenger_detail(detail_type, data):
    """
    Formats input data and then checks that it is of the expected type
    """

    # Create a dictionary with values to return to where function was called
    # Validity of data and formatted data are returned at the same time
    validated_info = {"validity": False, "data": None}
    
    # For each detail type, check that the input matches the expected data type
    try:
        if detail_type == "first name" or detail_type == "last name":
            formatted_info = data.capitalize()

            if not formatted_info.isalpha():
                raise ValueError("name must consist of letters only")

        elif detail_type == "date of birth":
            # Check that the input can be parsed to a datetime object
            input_date = datetime.strptime(data, '%Y-%m-%d').date()

            # Check that birth date is in the past
            today = datetime.now().date()
            if today <= input_date:
                raise ValueError("date of birth must be in the past")

            formatted_info = data
        
        elif detail_type == "passport no":
            formatted_info = data.upper()

            if not formatted_info.isalnum():
                raise ValueError("passport number must be letters and numbers only")

        elif detail_type == "nationality":
            formatted_info = data.upper()

            if formatted_info not in COUNTRIES:
                raise ValueError("must be a country name")
        
        elif detail_type == "luggage":
            formatted_info = int(data)

            if not (0 <= formatted_info <= 2):
                raise ValueError("number of luggage items must be between 0 and 2")
        
        else:
            print("Validation not yet available. Returning original value.")
            formatted_info = data

    except ValueError as e:
        print(f"Invalid data: {e}. Please try again.")
    
    else:
        # If not errors, set validity to True and add formatted data to return value
        validated_info["validity"] = True
        validated_info["data"] = formatted_info

    return validated_info


def main():
    """
    Main program. Allow user to choose which function(s) to run.
    """
    print(f"Welcome to Magnolia Airport's flight management portal.\n")
    print(f"What would you like to do?\n")

    control_options = {
        1: "view all passengers for a flight", 
        2: "book a ticket",
        3: "exit system"}

    for num, option in control_options.items():
        print(f"   {num}) {option.capitalize()}")

    while True:
        control_choice = input(f"\nType an option number here: ")

        try:
            int(control_choice)
        except ValueError:
            print("Please input a number")
        else:
            control_choice = int(control_choice)

            if control_choice == 1:
                view_all_passenger_details()
                break
            elif control_choice == 2:
                book_ticket()
                break
            elif control_choice == 3:
                print(f"\nGoodbye, have a nice day.")
                exit()
            else:
                print(f"No option ({control_choice}), please choose an option from the list above")
    
    input(f"Hit enter to return to the main program\n")
    main()


main()
