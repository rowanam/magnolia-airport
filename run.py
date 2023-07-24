import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('magnolia_airport')


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


def view_all_passenger_details(flight_number):
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
    # Ask for intended destination and check that there is a flight there
    while True:
        destination = input("What is the destination? ").capitalize()
        destinations_list = SHEET.worksheet("flights").col_values(2)[1:]

        readable_destinations_list = ", ".join(destinations_list)

        # If the desired destination not available, inform user of this and loop starts again
        # If the destination is available, loop breaks and function continues
        if destination not in destinations_list:
            print(f"""
No flights to {destination}.
Available destinations:

   {readable_destinations_list}

Please try again.
""")
        else:
            break
