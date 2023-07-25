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
    
    passenger_details = get_passenger_details()


def get_passenger_details():
    """
    Gets passenger details and returns them in a list
    """
    passenger_details = []
    details = ["first name", "last name", "date of birth", "passport no", "nationality"]

    # Get input for each required detail
    # Run detail through validator function and repeat request until correct data entered,
    # then append to passenger_details list
    for detail in details:
        while True:
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
    print("Validating...")

    # Create a dictionary with values to return to where function was called
    # Validity of data and formatted data are returned at the same time
    validated_info = {"validity": True, "data": None}

    def data_not_valid():
        """
        Changes validity in validated_info dictionary to False
        """
        validated_info["validity"] = False

    # For each detail type, first format data in the correct way for that type
    # Then check the input matches the expected data type
    if detail_type == "first name" or detail_type == "last name":
        formatted_info = data.capitalize()

        try:
            if formatted_info.isalpha():
                print("Data is valid.")
            else:
                data_not_valid()
                raise ValueError
        except ValueError:
            print("Invalid data, please try again.")

    # Will add validation steps for other detail types
    # For now, give the original input as return value so function can continue running
    else:
        print("Validation not yet available. Returning original value.")
        formatted_info = data

    validated_info["data"] = formatted_info

    return validated_info
