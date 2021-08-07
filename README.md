# MMO MANAGEMENT
#### Video Demo: https://youtu.be/D200VVHX7BI
#### Description:

This is a web-app made using Flask, HTML, CSS, Javascript and AJAX.
It was developed within the CS50 IDE, taking inspiration from the Pset-9 Finance App.

The purpose of this web-app is to make management of the non-profit easier and hassle-free.
From recording expenses to donations to keeping track of members and past donations and expenses.

##### Login Page
The login page is very simple, it takes in a username and password and
posts it as a form which is then validated by the backend python function that
checks to see if all fields are entered and whether or not the username and the
hash of the password entered matches with the coressponding username and password
hash in the database.

##### Register Page
The register page contains a form that takes in: username, umi, password and password
confirmation. The umi or Unique Member Identifier is given to every member of the org
and also present in the database so that while registering, the app can verify the user
that is registering is whether or not a member of the organization.

##### Index Page
This page and all other pages (exlucding the register page) require the user to be logged in.
The app welcomes the user and then a form is displayed which allows the user to create a
new event which is necessary to before recording any event expenses. This allows consistency
both throughout the app and the backened database that stores and links the events to their
respective details such as expenses, date and total expense.

##### Members Page
This page has a form that takes in MemberID as input which allows the user to view the data
available in the database for each member. The page also displays an overview of every member's
name and school by displaying them in table that is dynamically generated usiing Jinja.

##### Past Event Records
Here, the user can view an overview of the records of past events displayed in a table
or select an event from the form option field and view in-depth details of each event that
is present in the database and was created in the index page.

##### Record Event Expenses
This page allows the user to record expenses for an event, in three fields; item, quantity
and cost which is then displayed using Ajax and JQuery in a table below and rows are dynamically
added each time the user enters a new expense. This is the page that took me the longest as I wasn't
familiar with Ajax at the time and refreshing the page everytime the user entered a new expenses
wasn't really good user experience and neither was adding new forms rows. So finally, Ajax came
to the rescue and made the page function seamlessly.

##### Donors and Funds
This page allows the user to record donations and enter info such as donor name, source, date
and amount which is then entered into the database and displayed on a table below the form. The
user can also upload an image as proof which is stored in the database as a BLOB for future audit
purposes.
