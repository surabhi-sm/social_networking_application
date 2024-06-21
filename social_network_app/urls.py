from django.urls import path
from .views import user_signup,login,search_users_by_keyword,send_friend_request,friend_request_status,list_pending_friend_requests

urlpatterns = [
 path('user_signup/', user_signup, name='user_signup'),
 path('login/', login, name='login'),
 path('search_users_by_keyword/', search_users_by_keyword, name='search_users_by_keyword'),
 path('send_friend_request/', send_friend_request, name='send_friend_request'),
 path('friend_request_status/', friend_request_status, name='friend_request_status'),
 path('list_pending_friend_requests/',list_pending_friend_requests,name='list_pending_friend_requests'),
]
