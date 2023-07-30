# Magnolia Airport Passenger Management Portal

This program provides a simple command-line interface portal for a small regional airport somewhere in the southern United States. Flight details and booked passenger data is stored in a Google Sheets spreadsheet and the portal provides programs to view information, make bookings, change details and check in.

View the deployed program here - [link]() (not yet live)

ADD PICTURE

- program
![]()

## User Experience

The program is designed to be used by airport staff, for example at the check-in counter. Therefore it is not intended to be end user friendly and cuts down on explanations of questions and aesthetic additions in favor of serving a user who sees the same program every day.

However, the program should be intuitive and easy to use, and allow frictionless data entry and navigation between different programs.

### Moving through the portal

The portal opens with a menu of options, which the user can select to start different programs (book a ticket, check in, etc.).

Each program will ask one or more questions of the user, print data to the terminal, and provide options to complete certain tasks or return to the main program.

## Features

### All programs - user input

ADD PICTURE

- question
![]()

Throughout the program, a line of arrows is printed before prompts for user input as a visual signal to differentiate questions from printed lines of information. The same symbol is used throughout for consistency.

For every question, the program checks if the input given is of a type that was expected. Questions will repeat until a valid option or input type is provided.

### Start up banner

ADD PICTURE

- start up banner
![]()

On program start up, the terminal displays a welcome banner and prompts the user to press enter to open the portal.

### Main program

ADD PICTURE

- main menu
![]()

When the main program runs, a welcome message is printed onto the screen. Then a menu of program options is displayed and the user is prompted to select one.

### View all flights

ADD PICTURE

- view all flights
![]()

A table of all of the available flights is printed to the terminal, with relevant details for a person looking to book a flight.

The user is then asked if they want to book a ticket.
- 'yes' brings them to the ticket booking program
- 'no' returns them to the main page

### View all passengers for a flight

ADD PICTURE

- view all passengers for a flight
![]()

The user is asked to input a flight number, then details are printed for each passenger on the selected flight.

### Book ticket

ADD PICTURE

- book ticket
![]()

A list of available destinations is printed to the screen and the user is prompted to choose one. If they respond with a location not on the list, the list and prompt will appear again.

Flight info for all available flights to the chosen destination are printed to the terminal.
- If there is only one, the user will be asked if they want to book it
- If there are multiple, the details for each will be printed. The user will first be asked if any of the flights are acceptable, then if they answer 'yes', are prompted to select one

If the user says no available flights to the destination are acceptable, they will be given the option to choose another destination or return to the main program.

If a flight is selected, the program will continue with the booking and move to the passenger details page.

ADD PICTURE

- passenger details
![]()

A message is displayed on top to confirm which flight is being booked.

The user is prompted with a series of questions to gather relevant information about the passenger. Each question validates the input depending on the expected type of data:
- First/last names - required to have at least one letter and consist of letters, spaces and dashes ('-') only
- Date of birth - required to be a date, passed in the format YYYY-MM-DD, and must be a date in the past (before today)
- Passport no - must consist of letters and numbers only
- Nationality - must be a country in a country list taken from [pycountry](https://pypi.org/project/pycountry/)
- Luggage - must be a whole number between 0 and 2

ADD PICTURE

- screenshot of booking page with all information entered
![]()

If an invalid entry is provided, the terminal will display an error message in red explaining what the problem is, then ask the question again.

ADD PICTURE

- input error
![]()

After all data is entered correctly, the program randomly generates a booking number consisting of two letters, two numbers, two letters an two numbers (e.g. TF78RE32). This number is checked against a list of existing booking numbers, and if not already in the list is added itself, to ensure that booking numbers are not duplicated.

All of the passenger data and the booking number is added to a new row in the worksheet for the relevant flight in the Google Sheets spreadsheet.

ADD PICTURE

- flight worksheet before passenger added
![]()

ADD PICTURE

- flight worksheet after passenger added
![]()

The program then displays a message confirming that the booking was completed and prints the booking details to the terminal.

The user can then press enter to return to the main program.

### View and update passenger details

User is prompted to input the last name and booking number associated with a booking.

ADD PICTURE

- booking details input
![]()

If the last name does not match the booking, the user is given the option to try again or return to the main page.

ADD PICTURE

- booking name incorrect
![]()

If the booking number does not exist, the user is prompted to try inputting it again.

ADD PICTURE

- booking number incorrect
![]()

If a booking is found with the matched name and booking number, the passenger details are printed to the terminal. A message will then inform the user whether the passenger is already checked in.

ADD PICTURE

- passenger details
![]()

If the passenger is already checked in, the user will be informed that the passenger details can no longer be changed. They will then be given the option to add luggage to the booking (which can still be done after check in.) If they respond 'yes', they are taken to the luggage adding program, if 'no' back to the main program.

If the passenger is not yet checked in, the user will be asked if they want to update any details. If 'yes', they are taken to the update details page.

The program will prompt the user to enter the detail type to be changed. If they enter an invald detail type, a list will appear showing the options and the prompt is repeated.

ADD PICTURE

- choose a valid detail type to be changed
![]()

When a valid option is entered, the user will be asked to input the new data. This will then be validated in the same way as when a ticket is booked. If the data is valid, the information will be updated in the relevant flight worksheet.

ADD PICTURE

- worksheet before detail change
![]()

ADD PICTURE

- worksheet after detail change
![]()

In the terminal, a confirmation message will appear stating that the change has been made, and the old and new details will also be printed.

Then the user will hit enter to return to the main program.

### Check in

The user will be prompted to enter a last name and booking number, which will be checked in the same way as described above in the ticket booking program.

Once a booking is successfully found, the program will inform the user whether that passenger is already checked in.

ADD PICTURE

- passenger already checked in message
![]()

If the passenger is not yet checked in, the program will print a message warning that passenger details can no longer be changed after check in. The current passenger details will then be prompted and the user will be asked if anything needs to be updated.

ADD PICTURE

- warning and current passenger details
![]()

If details need to be changed, the user will be taken to the update details program, described above. After updating any necessary data, they will be returned and ask if they wish to continue checking in.

ADD PICTURE

- after details update continue check in q
![]()

If no details need to be changed, the passenger will be checked in. This will update the 'checked in' cell in their worksheet row to TRUE, and a message confirming the check in will be printed.

ADD PICTURE

- passenger checked in confirmation
![]()

### Add luggage

If a passenger is checked in, luggage can only be added, not removed, so this program allows the luggage data to be changed only by increasing the current value.

As above, the booking needs to be retrieved by last name and booking number.

The program then informs the user how much luggage is currently booked, and depending on the number, asks if the user wants to increase that amount or leave it the same.

ADD PICTURE

- add luggage question
![]()

If a new number is entered, this data is updated in the relevant worksheet, and in any case a message is displayed stating that the change has been made or that the luggage amount has been left at the original number.

ADD PICTURE

- confirm luggage change
![]()

### Exit portal

From the main menu, the user can exit the program by entering '100'.

ADD PICTURE

- exit portal
![]()

## Technologies Used

- [Git](https://gist.github.com/derhuerst/1b15ff4652a867391f03) for version control
- [GitHub](https://github.com/) to store project code
- [GitPod](https://www.gitpod.io/) for coding the project
- Heroku for project deployment
- [PIP](https://pip.pypa.io/en/stable/installation/) to install tools

### Imported modules/libraries

- [gspread](https://docs.gspread.org/en/v5.10.0/) for manipulating Google Sheets spreadsheet
- [google auth] * - add URL
- [pycountry](https://pypi.org/project/pycountry/) to get a list of world countries
- [termcolor](https://pypi.org/project/termcolor/) to print to the terminal in color
- [halo](https://github.com/manrajgrover/halo) to add spinning icons during loading
- [tabulate](https://pypi.org/project/tabulate/) to display information in tables

### Programming language

- [Python](https://www.python.org/)

## Google API Setup

Google Drive and Google Sheets APIs were used to link this project with a Sheets spreadsheet, allowing data to be read from the spreadsheet, manipulated and added.

## Bugs

### Booking different flight loop

Bug found 25.7.23

In the book_ticket function, the program asks if a certain flight time is ok, and if the user says "no", they are asked if they want to book another flight. If the user says "no" again, the book_ticket function ends and the main program body continues. On the other hand, if the user first says "yes", they want to book another ticket, the function is called again from the start. 

The function works if the user says "no" to both questions the first time. But here is the bug: if they first say "yes", they want to book another ticket, then say "no", that time doesn't work, and then "no", they don't want to book another ticket, the function doesn't end, and instead asks again if the user would like to book a different flight.

Bug fixed 26.7.23

Fixed the bug by adding a return statement in an if statement in an inner loop in the function. Right above this return statement, the entire function that was currently runnng was called again, which was intended to reset the current program but I believe instead created a second instance of that function running, and when that ended the first function instance kept runnng. Seems to be resolved by adding the return statement to stop the "first" function running after the second ends, but there is probably a more elegant solution.

### Name input validation

The first and las names validation test was changed to required that the user input at least one letter.

### From add luggage function, exit find booking

The find_booking function is set up to allow the user to try entering details again, or exit and return to the main menu if the booking cannot be found. It does this by returning the values None or 'main' to where the function was called. Two of the functions that called find_booking were set up to check for these returned values and so handled them correctly, but the add_luggage function, which also calls find_booking, did not have these checks set up and so if the user attempted to try again or exit to the main program the program threw an error. The issue was fixed by adding checks for None and 'main' return values after the function call in add_luggage.

## Testing

## Deployment

## Attributions

### Magnolia start-up banner

Magnolia outline in start-up banner was created by taking an image from Freepik (link below) and uploading it to ASCIIart.club.

Image by <a href="https://www.freepik.com/free-vector/hand-drawn-simple-flower-outline-illustration_24999034.htm#query=magnolia%20outline%20simple&position=0&from_view=search&track=ais">Freepik</a>

<a href="https://asciiart.club/">ASCIIart.club</a>

### Slow print function

Slow print function taken from this <a href="https://stackoverflow.com/questions/4099422/printing-slowly-simulate-typing">stackoverflow post.</a>