# Social Networking Application

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Setup](#setup)
  - [Creating a Virtual Environment](#creating-a-virtual-environment)
  - [Installing Requirements](#installing-requirements)
- [Running the Application](#running-the-application)
- [6 API's](#6_API'S)
  - [user_signup](#register_the_user)
  - [login](#user_login)
  - [Search Users by Keyword](#search-users-by-keyword)
  - [send_friend_request](send_friend_request)
  - [friend_request_status](friend_request_status)
  - [list_pending_friend_requests](list_pending_friend_requests)
- [Database_Connection](#Database_connection)
- [Postman_collection](#Postman_collection)


## Introduction
This is a social networking application built with Django and MongoDB. Users can signup, login and can send, receive, or reject the friend requests, view pending friend requests, and manage their social network.

## Features

- User signup
- Login
- Filter user by their username or email
- Send friend requests
- Accept or reject friend requests
- View pending friend requests
- Rate limiting: Users can send a maximum of 3 friend requests per minute

## Prerequisites

- Python 3.x
- pip (Python package installer)
- MongoDB

## Setup

## Creating a Virtual Environment
1. Open a terminal and navigate to the project directory.
    Clone the repository
    
    ```sh
    git clone https://github.com/your-username/social_networking_application.git
    cd social_networking_application

3. Run the following command to create a virtual environment:
   ```sh
   python -m venv venv

4. Activate the virtual environment:
     ```sh
    venv\Scripts\activate

## Installing Requirements
- With the virtual environment activated, install the required packages:
     ```sh
    pip install -r requirements.txt

## Running the Application
- Run the development server:
     ```sh
    python manage.py runserver

## 6 API's
- ### You can see all these api's in views.py file.

1. user_signup
    
    The provided API facilitates user signup by handling POST requests to register new users. It includes an email validation function to ensure that submitted email addresses adhere to a standard format. If the email is valid and not already in use, the new user details are inserted into a MongoDB collection. Additionally, it handles potential errors such as invalid JSON input and disallowed request methods.

2. login

    The login endpoint handles user authentication via POST requests. It accepts JSON data containing email and password, verifies their presence, and queries a database collection to find a matching user. If successful, it returns a "Login successful" message with a status code of 200; otherwise, it responds with "Invalid credentials" and a status code of 400. The endpoint is protected from CSRF attacks (@csrf_exempt) and only allows POST requests, rejecting other HTTP methods with a 405 status.

3. search-users-by-keyword


    The search_users_by_keyword function is designed to handle GET requests for searching users based on a provided keyword. It first extracts the keyword from the request body and validates its format. If the keyword resembles an email address, it constructs a query to search for users by email; otherwise, it searches for usernames that start with the specified keyword using a case-insensitive regex match. The function then retrieves usernames matching the query from a MongoDB collection and formats them into a JSON response. If no keyword is provided, it returns an error response indicating that the keyword is required. The function is CSRF exempt to facilitate cross-origin requests.

4. send_friend_request


    The send_friend_request API endpoint handles the process of sending a friend request between users in a system. It accepts POST requests containing JSON data specifying the sender's and recipient's usernames. Upon receiving a request, the endpoint verifies the existence of both users in a database collection. It checks if a friend request has already been sent from the sender to the recipient and ensures that the sender has not exceeded a limit on the number of requests sent per minute.

    If all checks pass, it creates a new friend request record and updates the recipient's document in the database to include this request. If successful, it returns a success message; otherwise, it returns appropriate error messages indicating missing data, user not found, existing request, or request limits exceeded. This endpoint is protected from CSRF attacks and responds with JSON formatted data based on the outcome of the request.

5. friend_request_status

    The friend_request_status API endpoint handles the status update of friend requests between users. It accepts POST requests with JSON data containing the status (accepted or rejected), the sender's username (from_username), and the recipient's username (to_username). It verifies the presence and validity of these fields and ensures both users exist in the database (collection). If the request is valid and the friend request status is successfully updated in the database, it returns a success message. Otherwise, it returns appropriate error responses for missing data, invalid status values, user not found, or failed database updates. This endpoint is crucial for managing friend requests within the application.

6. list_pending_friend_requests

    This API endpoint, list_pending_friend_requests, handles GET requests to retrieve pending friend requests for a specified user. It expects a JSON payload containing a username. Upon receiving the request, it verifies the presence of the username and retrieves the user object from a database collection. If the user exists, it filters out and returns all pending friend requests associated with that user. The response includes a JSON array of pending friend requests, ensuring any database-specific IDs are converted to string format for consistency. This endpoint is protected against Cross-Site Request Forgery (CSRF) attacks using the @csrf_exempt decorator.

## Database Connection
The MongoDB connection string is located in the .env file. You can use this string to connect to the database using MongoDB Compass or Atlas.

## Postman collection
The Postman collection file will be available in the Git repository. You can use it to execute all six APIs.
