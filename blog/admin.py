from django.contrib import admin
from .models import CustomUser, Post, Comment, Vote, Conversation, Message

admin.site.register(CustomUser)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Vote)
admin.site.register(Conversation)
admin.site.register(Message)
