## Bugs

### Booking different flight loop
On 25.7.
In the book_ticket function, the program asks if a certain flight time is ok, and if the user says "no", they are asked if they want to book another flight. If the user says "no" again, the book_ticket function ends and the main program body continues. On the other hand, if the user first says "yes", they want to book another ticket, the function is called again from the start. 

The function works if the user says "no" to both questions the first time. But here is the bug: if they first say "yes", they want to book another ticket, then say "no", that time doesn't work, and then "no", they don't want to book another ticket, the function doesn't end, and instead asks again if the user would like to book a different flight.

26.7
Fixed the bug by adding a return statement in an if statement in an inner loop in the function. Right above this return statement, the entire function that was currently runnng was called again, which was intended to reset the current program but I believe instead created a second instance of that function running, and when that ended the first function instance kept runnng. Seems to be resolved by adding the return statement to stop the "first" function running after the second ends, but there is probably a more elegant solution.

## Attributions

### Magnolia start-up banner

Magnolia outline in start-up banner was created by taking an image from Freepik (link below) and uploading it to ASCIIart.club.

Image by <a href="https://www.freepik.com/free-vector/hand-drawn-simple-flower-outline-illustration_24999034.htm#query=magnolia%20outline%20simple&position=0&from_view=search&track=ais">Freepik</a>

<a href="https://asciiart.club/">ASCIIart.club</a>

### Slow print function

Slow print function taken from this <a href="https://stackoverflow.com/questions/4099422/printing-slowly-simulate-typing">stackoverflow post.</a>