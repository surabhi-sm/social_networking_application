from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.http import JsonResponse
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
import json
import re
import os
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['user']  # Database name
collection = db['user_signup']  # Collection name

# Simple email validation function
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

@csrf_exempt
def user_signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')

            # Validate email
            if not is_valid_email(email):
                return JsonResponse({'error': 'Invalid email address'}, status=400)

            # Check if the user already exists
            if collection.find_one({"email": email}):
                return JsonResponse({'error': 'Email already exists'}, status=400)

            # Insert new user into MongoDB
            new_user = {
                "username": username,
                "password": password,  # In a real application, make sure to hash passwords!
                "email": email
            }
            collection.insert_one(new_user)
            return JsonResponse({'message': 'User registered successfully'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({"error": "Email and password are required"}, status=400)

            user = collection.find_one({"email": email,"password":password})
     
            if user:
                return JsonResponse({"message": "Login successful"}, status=200)
            else:
                return JsonResponse({"error": "Invalid credentials"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


@csrf_exempt
def search_users_by_keyword(request):
    if request.method == 'GET':
        data = json.loads(request.body)
        keyword = data.get('keyword')

        if keyword:
            # Check if the keyword is an email format
            if re.match(r"[^@]+@[^@]+\.[^@]+", keyword):
                query = {'email': keyword}
            else:
                # Match usernames that start with the keyword
                query = {'username': {'$regex': f'^{keyword}', '$options': 'i'}}
            
            cursor = collection.find(query, {'username': 1, '_id': 0})

            # Format the response
            data_list = [item['username'] for item in cursor]
            
            return JsonResponse({"usernames": data_list}, safe=False)
        else:
            return JsonResponse({"error": "Keyword is required"}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def send_friend_request(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        from_username = data.get('from_username')
        to_username = data.get('to_username')

        if not from_username or not to_username:
            return JsonResponse({'error': 'Missing from_username or to_username'}, status=400)

        from_user = collection.find_one({'username': from_username})
        to_user = collection.find_one({'username': to_username})

        if not from_user or not to_user:
            return JsonResponse({'error': 'User not found'}, status=404)

        from_user_id = from_user['_id']
        from_user = from_user['username']
        to_user_id = to_user['_id']

        # Check for existing friend request
        existing_request = collection.find_one({
            'username': to_username,
            'friend_requests': {
                '$elemMatch': {
                    'friend_request_from': from_user,
                    'status': 'pending'
                }
            }
        })

        if existing_request:
            return JsonResponse({'error': 'Friend request already sent'}, status=400)

        # Check the number of requests sent in the last minute across all users
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        recent_requests = collection.aggregate([
            {'$match': {'friend_requests.friend_request_from': from_user}},
            {'$unwind': '$friend_requests'},
            {'$match': {'friend_requests.timestamp': {'$gte': one_minute_ago}}},
            {'$count': 'recent_requests_count'}
        ])

        recent_requests_count = next(recent_requests, {}).get('recent_requests_count', 0)

        if recent_requests_count >= 3:
            return JsonResponse({'error': 'Too many friend requests sent in the last minute'}, status=429)

        # Create the friend request
        friend_request = {
            'friend_request_from_id': from_user_id,
            'friend_request_from': from_user,
            'status': 'pending',
            'timestamp': datetime.utcnow()
        }

        update_result = collection.update_one(
            {'_id': to_user_id},
            {'$push': {'friend_requests': friend_request}}
        )

        if update_result.modified_count == 0:
            return JsonResponse({'error': 'Friend request not sent'}, status=500)
        
        return JsonResponse({'message': 'Friend request sent successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def friend_request_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        status = data.get('status')
        from_username = data.get('from_username')
        to_username = data.get('to_username')

        if not status or not from_username or not to_username:
            return JsonResponse({'error': 'Missing status, from_username, or to_username'}, status=400)

        if status not in ['accepted', 'rejected']:
            return JsonResponse({'error': 'Invalid status value'}, status=400)

        from_user = collection.find_one({'username': from_username})
        to_user = collection.find_one({'username': to_username})
        
        if not from_user or not to_user:
            return JsonResponse({'error': 'User not found'}, status=404)

        update_result = collection.update_one(
            {'username': to_username, 'friend_requests.friend_request_from': from_username},
            {'$set': {'friend_requests.$.status': status}}
        )
        if update_result.modified_count == 0:
            return JsonResponse({'error': 'Friend request not found or status not updated'}, status=500)

        return JsonResponse({'message': f'Friend request {status}'}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def convert_objectid_to_str(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_objectid_to_str(value) for key, value in obj.items()}
    else:
        return obj

@csrf_exempt
def list_pending_friend_requests(request):
    if request.method == 'GET':
        data = json.loads(request.body)
        username = data.get('username')

        if not username:
            return JsonResponse({'error': 'Missing username'}, status=400)

        user = collection.find_one({'username': username})

        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)

        pending_requests = [
            req for req in user.get('friend_requests', []) if req['status'] == 'pending'
        ]

        # Convert the entire user object to ensure no ObjectId remains
        pending_requests = convert_objectid_to_str(pending_requests)

        return JsonResponse({'pending_friend_requests': pending_requests}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=405)




