from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from blog import views

urlpatterns = [
                  # Home and Post-related URLs
                  path('', views.home, name='home'),  # Home page
                  path('post/<int:post_id>/', views.post_detail, name='post_detail'),  # Post detail page
                  path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),  # Add comment
                  path('post/<int:post_id>/update/', views.update_post, name='update_post'),  # Update post
                  path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),  # Delete post
                  path('post/<int:post_id>/upvote/', views.upvote_post, name='upvote_post'),  # Upvote post
                  path('post/<int:post_id>/downvote/', views.downvote_post, name='downvote_post'),  # Downvote post
                  path('comment/<int:comment_id>/update/', views.update_comment, name='update_comment'),
                  # Update comment
                  path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
                  # Delete comment
                  path('comment/<int:comment_id>/upvote/', views.upvote_comment, name='upvote_comment'),
                  # Upvote comment
                  path('comment/<int:comment_id>/downvote/', views.downvote_comment, name='downvote_comment'),
                  # Downvote comment

                  # User Authentication URLs
                  path('register/', views.register, name='register'),  # User registration
                  path('login/', views.login_view, name='login'),  # User login
                  path('logout/', views.logout_view, name='logout'),  # User logout

                  # User Profile URLs
                  path('main/', views.main_view, name='main'),  # Main page after login
                  path('profile/<str:username>/', views.profile, name='profile'),  # User profile page
                  path('profile/<str:username>/edit/', views.edit_profile, name='edit_profile'),  # Edit profile

                  # Chat-related URLs
                  path('conversation/<int:conversation_id>/', views.conversation_view, name='conversation_view'),
                  path('start_conversation/<int:user_id>/', views.start_conversation, name='start_conversation'),
                  path('chats/', views.chat_list_view, name='chat_list'),
                  path('search_user/', views.search_user, name='search_user'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Serve media files during development
