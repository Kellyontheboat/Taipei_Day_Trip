# Taipei Attraction Tour Backend

This project is designed to help users browse and book tours of Taipei's attractions. It allows users to filter attractions by MRT stations or keywords, view detailed information about each attraction, and manage their tour selections in a shopping cart. Users can securely pay for their tours using a credit card and receive an order number upon successful payment.

## Features

1. **Browse Attractions**: 
   - Users can explore various Taipei attraction spots.
   - Filter attractions by MRT stations or user-entered keywords.

https://github.com/user-attachments/assets/87bdde68-76ec-44c2-a6c6-47d6119d5e55


2. **Attraction Details and Booking**:
   - View detailed information about each attraction.
   - Select a time slot and add the tour to a shopping cart.

https://github.com/user-attachments/assets/3b3429d4-9bbc-418e-a621-47d853934cb9


3. **Secure Payment**:
   - After finalizing selections in the shopping cart, users can pay using a credit card.
   - Receive an order number upon successful payment.
   - Test card number: `4242 4242 4242 4242` Test CVV: `123`(use any future expiry date).


https://github.com/user-attachments/assets/70c78241-d4cd-464f-bb07-ea3b3b7df284


## Technical Highlights

- **Backend Framework**: Built using Python with FastAPI for efficient and scalable server-side operations.
- **Authentication**: Implemented JWT for secure user authentication and session management.
- **Payment Processing**: Integrated TapPay for secure and reliable payment transactions.
- **Database Management**: 
  - Utilized MySQL Connector/Python with a connection pool for stable and efficient database interactions.
  - Enhanced performance with database indexing and minitoring improvments with EXPLAIN.
- **Responsive Design**: Applied Responsive Web Design (RWD) principles to ensure the application is accessible and user-friendly across various device sizes.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
