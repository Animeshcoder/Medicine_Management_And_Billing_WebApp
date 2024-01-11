Project: Medicine Management and Billing System

This project is a web-based application developed using Flask, a Python web framework. The application serves as a medicine management and billing system with the following features:

User Authentication: The application uses Flask-Login for user management. It provides user session management for Flask: handling the common tasks of logging in, logging out, and remembering users’ sessions over extended periods.

Database Interaction: The application uses PyMySQL to interact with a MySQL database. It fetches and manipulates data related to medicines.

Medicine Search: Users can search for medicines. The search results are fetched from the database and displayed on the webpage.

Medicine Details: Users can view detailed information about a specific medicine. The information is retrieved from the database based on the medicine’s ID.

Billing: The application includes a billing feature. Users can select a medicine and specify a quantity to generate a bill. The bill details are sent to a specified phone number using the Twilio service.

SMS Notifications: The application uses the Twilio API to send SMS notifications. When a bill is generated, an SMS notification is sent to the provided phone number.

This project demonstrates a practical application of web development, database management, and third-party APIs. It could be particularly useful for pharmacies and medical stores for managing their medicine inventory and billing operations. The use of SMS notifications enhances the user experience by providing real-time updates.
