import gspread
from google.oauth2.service_account import Credentials

import random
import string

from datetime import datetime

from pycountry import countries

from termcolor import colored, cprint

import os


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

# Print in red or green to terminal, for error or success messages
PRINT_RED = lambda x: cprint(x, "red")
PRINT_GREEN = lambda x: cprint(x, "green")


def clear():
    """
    Clears terminal
    """
    os.system("clear")


def type_yes_no():
    """
    Micro function to tell user to input 'yes' or 'no' only
    """
    PRINT_RED(f"Please type 'yes' or 'no' only.\n")


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
    name = f"{passenger['first name(s)']} {passenger['last name']}"
    readable_details = name

    # Add line for each detail except first and last name to string
    for key, value in passenger.items():
        if key == "first name(s)" or key == "last name" or key == "checked in":
            continue
        
        readable_details += (f"\n   {key.capitalize()}: {value}")

    readable_details += f"\n"

    passenger_info = {
        "name": name,
        "readable_details": readable_details
    }
    
    return passenger_info


def create_heading(title):
    """
    Print a heading to the terminal to visually signify starting a function
    """
    heading = f"""
----------------------------------------
{title}
----------------------------------------
    """

    return heading


def format_flight_date(date_str):
    """
    Pass a date string in format YYYY-MM-DD, returns in format e.g. Jun 23, 2023
    """
    flight_date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
    formatted_flight_date = flight_date_object.strftime("%b %-d, %Y")

    return formatted_flight_date


def view_all_flights():
    """
    Gets all available flights and returns as a readable string
    """
    clear()
    print(create_heading("View Flights"))

    print(f"Retrieving flights...\n")

    all_flights = FLIGHTS_WS.get_all_records()
    
    flights_details_lines = []

    for flight in all_flights:
        destination = flight["destination"]
        date = format_flight_date(flight["date"])
        departure_time = flight["departure time"]
        flight_no = flight["flight no"]

        flight_line = f"   {destination}: on {date} at {departure_time}, flight no. {flight_no}\n"
        flights_details_lines.append(flight_line)
    
    flights_details_string = "\n".join(flights_details_lines)

    readable_flights_list = f"Flight to...\n\n" + flights_details_string
    print(readable_flights_list)

    while True:
        book_a_ticket = input("Would you like to make a booking? (yes/no) ")

        if book_a_ticket == "yes":
            print("Taking you to ticket booking program...")
            ticket_booking_program()
            return
        elif book_a_ticket == "no":
            print("Exiting flight viewing...")
            return
        else:
            type_yes_no()


def view_all_passengers_of_flight():
    """
    Asks the user for a flight number, then prints a readable output of all
    passengers on that flight and their details
    """
    clear()
    print(create_heading("View All Flight Passengers"))

    flight_nos_column = get_flights_ws_column_no("flight no")
    flight_nos = FLIGHTS_WS.col_values(flight_nos_column)

    while True:
        flight = input("Please input a flight number: ")

        try:
            if flight in flight_nos:
                print(f"\n", get_all_passengers_of_flight(flight))
                break
            else:
                raise ValueError("Invalid flight number")
        except ValueError as e:
            PRINT_RED(f"{e}, please try again\n")


def get_all_passengers_of_flight(flight_number):
    """
    View all passengers and their details on the flight with the provided number
    """
    worksheet_to_view = SHEET.worksheet(flight_number)

    # Get passenger info as a list of dictionaries
    passengers = worksheet_to_view.get_all_records()

    passengers_display_string = ""

    for passenger in passengers:
        details = readable_passenger_details(passenger)["readable_details"]
        passengers_display_string += f"{details}\n"
    
    return passengers_display_string


def ticket_booking_program():
    """
    Starts the ticket booking program
    """
    clear()
    print(create_heading("Ticket Booking"))

    book_ticket()


def book_ticket():
    """
    Add a new passenger to a flight.
    Will ask for user input to determine which flight they want to book
    and get passenger details.
    """

    # From spreadsheet, pull all flight destinations
    destinations_column = get_flights_ws_column_no("destination")
    destinations_list = FLIGHTS_WS.col_values(destinations_column)[1:]
    destinations_set = set(destinations_list)

    # Make destinations readable
    destinations_alphabetized = sorted(destinations_set)
    readable_destinations_list = ", ".join(destinations_alphabetized)
    view_available_destinations = f"""Available destinations:

---
{readable_destinations_list}
---
"""

    print(view_available_destinations)

    # Ask for intended destination and check that there is a flight there
    while True:
        # Get user input for flight destination
        destination = input("Select a destination: ").capitalize()

        # If the desired destination not available, inform user of this and loop starts again
        # If the destination is available, loop breaks and function continues
        if destination not in destinations_set:
            PRINT_RED(f"\nNo flights to {destination}.")
            print(f"""
{view_available_destinations}

Please try again.
""")
        else:
            break

    print(f"\nSearching for dates...")

    # Get all flights to chosen destination and number of flights
    flights_to_destination = FLIGHTS_WS.findall(destination)
    no_of_flights = len(flights_to_destination)


    def get_date_and_time(flight_row):
        """
        Retrieve the date and time of flight in passed row
        """
        flight_times_column = get_flights_ws_column_no("departure time")
        flight_dates_column = get_flights_ws_column_no("date")
        flight_time = FLIGHTS_WS.cell(flight_row, flight_times_column).value
        flight_date = FLIGHTS_WS.cell(flight_row, flight_dates_column).value
        readable_flight_date = format_flight_date(flight_date)

        flight_details = {
            "date": readable_flight_date,
            "time": flight_time
        }

        return flight_details


    # Variable "flight_row" determines which flight the passenger gets added to
    # Based on number of available flights to destination:
    # - if only one flight, assign flight_row to the row of that flight
    # - if multiple available flights, show the available flights, 
    #   and later will ask user to choose, and assigns that to flight_row
    # In either case, ask the user if the flight options are ok
    if no_of_flights == 1:
        flight_row = flights_to_destination[0].row
        flight_details = get_date_and_time(flight_row)
        time = flight_details["time"]
        date = flight_details["date"]

        report_flight_info = f"We have a flight to {destination} on {date} at {time}."
        continue_booking_q = "Is that ok? (yes/no): "
    else:
        flight_rows = [flight.row for flight in flights_to_destination]
        flights_details = [get_date_and_time(row) for row in flight_rows]
        
        report_flight_info = f"We have flights to {destination} on:"

        for flight in flights_details:
            report_flight_info += f"\n   - {flight['date']} at {flight['time']}"

        continue_booking_q = "Is one of those ok? (yes/no): "

    # Ask user if the flight at a certain time should be booked,
    # or to choose between multiple flights
    # If yes, continue booking
    # If no acceptable flights, function stops and code returns to main program
    while True:
        # Show flights information and ask for user input depending on number of flights
        print(f"\n{report_flight_info}")
        continue_booking = input(f"\n{continue_booking_q}")

        # Continue booking if there is an acceptable flight
        if continue_booking.lower() == "yes":
            # If only one flight, continue with that flight
            if no_of_flights == 1:
                break
            # If multiple available flights, choose one then continue booking
            else:
                while True:
                    print(f"\nChoose a flight...")

                    for flight in flights_details:
                        print(f"   {flights_details.index(flight) + 1}) {flight['date']} at {flight['time']}")

                    flight_option = input(f"\nType the number: ")

                    try:
                        flight_option_index = int(flight_option) - 1
                        flight_row = flight_rows[flight_option_index]
                    except:
                        PRINT_RED("Please type one of the numbers above.")
                    else:
                        break
                
                break
        
        # If displayed flights are not acceptable, ask whether to book a different flight
        # or return to main menu
        elif continue_booking.lower() == "no":
            while True:
                new_request = input(f"\nWould you like to book a different flight? (yes/no) ")

                if new_request.lower() == "yes":
                    print()
                    book_ticket()
                    # After re-calling function above, first time function call is still running,
                    # and will come back to this loop when the second function call stops.
                    # This return means that when the main function call comes back here,
                    # it will end
                    return
                elif new_request.lower() == "no":
                    print(f"\nExiting ticket booking...")
                    return
                else:
                    type_yes_no()
        
        # Prompt user to answer yes or no only
        else:
            type_yes_no()

    # Create a message to display flight info on passenger details page
    chosen_flight_details = get_date_and_time(flight_row)
    chosen_flight_date = chosen_flight_details["date"]
    chosen_flight_time = chosen_flight_details["time"]
    get_details_message = f"Booking a ticket bound for {destination}: {chosen_flight_date} at {chosen_flight_time}"
        
    # Ask user questions to get passenger details
    passenger_details = get_all_passenger_details(get_details_message)

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

    clear()

    PRINT_GREEN(f"\nPassenger {passenger_details[0]} {passenger_details[1]} successfully added to flight {flight_number}")

    # 's' suffix for 0 or 2 luggage pieces
    suffix = "s"
    if passenger_details[5] == 1:
        suffix = ""

    booking_confirmation_message = f"""

----------------------------------------
BOOKING DETAILS

Flight no. {flight_number} to {destination} on {chosen_flight_date} at {chosen_flight_time}

Name: {passenger_details[0]} {passenger_details[1]}
Booking no: {passenger_details[6]}
Luggage: {passenger_details[5]} piece{suffix}
----------------------------------------
    """

    print(booking_confirmation_message)
    print(f"Note: passenger details can be updated at any time until check in.\n")


def get_all_passenger_details(message):
    """
    Gets passenger details and returns them in a list
    """
    clear()
    print(create_heading("Passenger Details"))
    print(message)

    passenger_details = []
    details = ["first name(s)", "last name", "date of birth", "passport no", "nationality", "luggage"]

    # Get input for each required detail then append to passenger_details list
    for detail in details:
        data = get_passenger_detail(detail)
        passenger_details.append(data)
        
    return passenger_details


def get_passenger_detail(detail_type):
    """
    Gets user input for a passenger detail and validates the data
    """
    while True:
        # Print appropriate question for each detail type
        if detail_type == "date of birth":
            info = input(f"\nPlease enter {detail_type} (YYYY-MM-DD): ")
        elif detail_type == "nationality":
            print(f"\nNationality:")
            print("   If input country name doesn't work, please try writing it")
            print("   a different way (e.g. for UK type United Kingdom).")
            info = input(f"\nPlease enter {detail_type}: ")
        elif detail_type == "luggage":
            info = input(f"\nHow many items of checked luggage would you like to book? (max. 2) ")
        else:
            info = input(f"\nPlease enter {detail_type}: ")
        
        # Check that input data is valid
        validated_info = validate_passenger_detail(detail_type, info)

        data_is_valid = validated_info["validity"]
        if data_is_valid:
            break

    validated_data = validated_info["data"]

    return validated_data


def validate_passenger_detail(detail_type, data):
    """
    Formats input data and then checks that it is of the expected type
    """

    # Create a dictionary with values to return to where function was called
    # Validity of data and formatted data are returned at the same time
    validated_info = {"validity": False, "data": None}
    
    # For each detail type, check that the input matches the expected data type
    try:
        if detail_type == "first name(s)" or detail_type == "last name":
            formatted_info = data.title().strip()

            contains_letter = False
            for i in formatted_info:
                if i.isalpha():
                    contains_letter = True

            if not contains_letter:
                raise ValueError("name must contain at least one letter")
            elif not all(ch.isalpha() or ch.isspace() or ch == "-" for ch in formatted_info):
                raise ValueError("name must consist of letters, spaces and '-' only")

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
        PRINT_RED(f"Invalid data: {e}.\nPlease try again.")
    
    else:
        # If not errors, set validity to True and add formatted data to return value
        validated_info["validity"] = True
        validated_info["data"] = formatted_info

    return validated_info


def find_booking():
    """
    Ask user for last name and booking no and return flight no, booking no and passenger row number
    """
    details = {
        "flight_no": None,
        "booking_no": None,
        "row": None
    }

    entered_last_name = input("Please enter last name: ")

    # Get a list of all flight worksheets
    all_flight_worksheets = SHEET.worksheets()[2:]

    # Ask user for booking number and search for it in all flight worksheets
    while True:
        booking_no = input("Please enter the booking number: ")

        print(f"\nSearching for booking...")

        flight_no = None
        
        # Search for booking number. If found, assign the flight number to flight_no
        for flight_ws in all_flight_worksheets:
            found = bool(flight_ws.find(booking_no))
            
            if found:
                flight_no = flight_ws.title
        
        if flight_no:
            break
        else:
            PRINT_RED(f"Booking number not found. Please try again.\n")

    ws = SHEET.worksheet(flight_no)

    # Get the last name entered in the booking
    last_name_column = ws.find("last name").col
    row = ws.find(booking_no).row
    booking_last_name = ws.cell(row, last_name_column).value

    # Check if last name input matches last name in booking
    if entered_last_name != booking_last_name:
        PRINT_RED(f"Last name does not match booking.\n")

        # Return to where the function was called, passing either None or "main"
        # Original function will either call again or return to main() function
        while True:
            choice = input("Press 1 to try again or 2 to return to main page: ")

            if choice == "1":
                return
            elif choice == "2":
                return "main"
            else:
                PRINT_RED(f"Please type 1 or 2 only.\n")

    details["flight_no"] = flight_no
    details["booking_no"] = booking_no
    details["row"] = row

    return details


def view_passenger_details():
    """
    View a passenger's booking details and ask if anything needs to be changed
    if not already checked in
    """
    clear()
    print(create_heading("View Passenger Details"))

    # Get passenger details and continue based on return value
    while True:
        booking = find_booking()

        # If no passenger found, run the loop again and call find_booking()
        if booking == None:
            pass
        # If find_booking() returned "main", end current function and return to main function
        elif booking == "main":
            return
        # Otherwise, continue with current function
        else:
            break

    ws = SHEET.worksheet(booking["flight_no"])
    row = booking["row"]

    # Get passenger details as dict
    # Subtract 2 from row number because:
    # - When retrieving ws data as dict, row 1 is used as keys, i.e. one less item in returned list
    # - Rows start at 1, need to subtract a further unit for list indices starting at 0
    passenger = ws.get_all_records()[row - 2]

    formatted_passenger_info = readable_passenger_details(passenger)
    name = formatted_passenger_info["name"]

    print(f"\nPassenger details:\n")
    print(formatted_passenger_info["readable_details"])

    checked_in = see_if_checked_in(ws, row)

    if checked_in:
        PRINT_GREEN(f"{name} is already checked in. Passenger details can no longer be changed.\n")
    else:
        PRINT_RED(f"Not yet checked in.\n")

        while True:
            update_details = input("Update passenger details? (yes/no) ").lower()

            if update_details == "yes":
                update_passenger_details_program(ws, row, name)
                return
            elif update_details == "no":
                print("Exiting passenger details program...")
                return
            else:
                type_yes_no()


def update_passenger_details_program(ws, row, name):
    """
    Starts the program to update passenger details
    """
    clear()
    print(create_heading("Update Passenger Details"))

    # Ask the user what to change and update detail in ws
    get_new_passenger_detail(ws, row, name)


def get_new_passenger_detail(ws, row, name):
    """
    Change passenger details
    """

    # Get list of all column heading detail types that can be updated (excludes booking no and checked in cells)
    detail_types = ws.row_values(1)[:6]

    # Ask user to choose a detail type to be changed
    while True:
        detail_type_to_update = input("What detail needs to be changed? ").strip()

        if detail_type_to_update in detail_types:
            break
        elif detail_type_to_update == "none":
            print("Exiting update details program...")
            return
        else:
            print(f"\nDetail must be one of the following:")

            for detail in detail_types:
                print(f"   - {detail}")

            print(f"\nTo return to the main program, type 'none'")

            PRINT_RED(f"\nPlease try again.\n")

    # Get and validate user input for updated passenger data
    new_passenger_detail = get_passenger_detail(detail_type_to_update)

    # Update detail in ws
    detail_column = ws.find(detail_type_to_update).col
    update_passenger_detail_in_ws(ws, row, detail_column, new_passenger_detail, name)

    # See if user wants to change another detail
    while True:
        another_detail = input("Change another passenger detail? (yes/no) ")

        if another_detail == "yes":
            get_new_passenger_detail(ws, row, name)
            return
        elif another_detail == "no":
            print("Exiting update details program...")
            return
        else:
            type_yes_no()


def update_passenger_detail_in_ws(ws, row, column, data, name):
    """
    Update a passenger's booking detail in flight ws
    """
    print(f"\nUpdating passenger data...")

    # Get the original value to show user the change
    original_value = ws.cell(row,column).value

    # Update detail in ws
    ws.update_cell(row, column, data)

    # Get detail type from heading
    detail_type = ws.cell(1, column).value

    PRINT_GREEN(f"\n{detail_type.capitalize()} successfully updated for {name}.")

    print(f"\nOriginal input: {original_value}")
    print(f"New value: {data}\n")


def see_if_checked_in(ws, row):
    """
    Checks if a passenger has already checked in
    """
    checked_in_column = ws.find("checked in").col
    checked_in_cell = ws.cell(row, checked_in_column)

    # See if passenger is checked in by getting the boolean value of their "checked in" cell
    checked_in = bool(checked_in_cell.value)

    if checked_in:
        return True


def check_in():
    """
    Check a passenger in
    """
    clear()
    print(create_heading("Check In"))

    # Get passenger details and continue based on return value
    while True:
        passenger_details = find_booking()

        # If no passenger found, run the loop again and call find_booking()
        if passenger_details == None:
            pass
        # If find_booking() returned "main", end check_in and return to main function
        elif passenger_details == "main":
            return
        # Otherwise, continue with check in
        else:
            break

    # Store ws and booking info in variables
    ws = SHEET.worksheet(passenger_details["flight_no"])
    row = passenger_details["row"]
    booking_no = passenger_details["booking_no"]

    # Get passenger name and store as a string
    first_name_column = ws.find("first name(s)").col
    last_name_column = ws.find("last name").col
    first_name = ws.cell(row, first_name_column).value
    last_name = ws.cell(row, last_name_column).value
    name = f"{first_name} {last_name}"

    print(f"\nFor booking no. {booking_no} found passenger name: {name}")

    # Check that correct passenger has been retrieved
    while True:
        correct_passenger = input(f"\nIs this correct? (yes/no) ").lower()

        if correct_passenger == "yes":
            break
        elif correct_passenger == "no":
            print("Returning to home...")
            return
        else:
            type_yes_no()

    # See if passenger is already checked in
    checked_in = see_if_checked_in(ws, row)

    if checked_in:
        PRINT_GREEN(f"\n{name} is already checked in.")
        return

    print(f"\nChecking in...")
    
    # Update checked in cell value to True
    checked_in_column = ws.find("checked in").colchecked_in_column = ws.find("checked in").col
    ws.update_cell(row, checked_in_column, True)

    PRINT_GREEN(f"\n{name} successfully checked in")


def add_luggage():
    """
    Add luggage to a booking
    """
    clear()
    print(create_heading("Add Luggage"))

    passenger_details = find_booking()

    flight_ws = SHEET.worksheet(passenger_details["flight_no"])
    passenger_row = passenger_details["row"]

    # Lugagge = column 6
    current_luggage = int(flight_ws.cell(passenger_row, 6).value)

    if current_luggage == 2:
        PRINT_GREEN(f"\nPassenger already has 2 pieces of luggage, which is the maximum.")
    
    elif current_luggage == 1:
        print(f"\nPassenger currently has 1 piece of lugagge.")

        while True:
            add_luggage = input("Add 1 more? (yes/no): ").lower()

            if add_luggage == "yes":
                print(f"\nAdding luggage to booking...")

                flight_ws.update_cell(passenger_row, 6, 2)

                PRINT_GREEN(f"\n1 piece of luggage successfully added.")
                return
            elif add_luggage == "no":
                PRINT_GREEN(f"\nBooking left at 1 piece of luggage.")
                return
            else:
                type_yes_no()
    
    elif current_luggage == 0:
        print(f"\nPassenger currently has no checked luggage booked.")

        while True:
            more_luggage = input(f"\nHow many pieces of luggage should be added? ")

            if more_luggage == "0" or more_luggage == "none":
                PRINT_GREEN(f"\nBooking left at with no checked luggage.")
                return
            elif more_luggage == "1" or more_luggage == "2":
                print(f"\nAdding luggage to booking...")

                flight_ws.update_cell(passenger_row, 6, more_luggage)

                PRINT_GREEN(f"\nLuggage successfully added.")
                return
            else:
                type_yes_no()


def start_program():
    """
    Program start up. Print banner and call main() function.
    """
    clear()

    # Open the start-up banner
    with open("banner.txt") as f:
        banner = f.read()

    # Print colored start-up banner
    colored_banner = colored(banner, "black", "on_light_cyan")
    print(colored_banner)

    input("(Press enter) ")

    main()


def main():
    """
    Main program. Allow user to choose which function(s) to run.
    """
    clear()

    print(f"\n\nWelcome to Magnolia Airport's flight management portal.\n\n")
    print(f"What would you like to do?\n")

    control_options = {
        1: "view all flights",
        2: "view all passengers for a flight", 
        3: "book a ticket",
        4: "view and update passenger details",
        5: "check in a passenger",
        6: "add luggage",
        100: "exit system"}

    for num, option in control_options.items():
        if num == 100:
            print(f"\n   {num}) {option.capitalize()}")
        else:
            print(f"   {num}) {option.capitalize()}")

    while True:
        control_choice = input(f"\nType an option number here: ")

        try:
            int(control_choice)
        except ValueError:
            PRINT_RED("Please input a number")
        else:
            control_choice = int(control_choice)

            if control_choice == 1:
                view_all_flights()
                break
            elif control_choice == 2:
                view_all_passengers_of_flight()
                break
            elif control_choice == 3:
                ticket_booking_program()
                break
            elif control_choice == 4:
                view_passenger_details()
                break
            elif control_choice == 5:
                check_in()
                break
            elif control_choice == 6:
                add_luggage()
                break
            elif control_choice == 100:
                print(f"\nGoodbye, have a nice day.")
                exit()
            else:
                PRINT_RED(f"No option ({control_choice}), please choose an option from the list above")
    
    input(f"\nHit enter to return to the main program\n")
    main()


start_program()
