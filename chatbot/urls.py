from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('new-conversation/', views.new_conversation, name='new_conversation'),
    path('delete-conversation/<int:conversation_id>/', views.delete_conversation, name='delete_conversation'),
]