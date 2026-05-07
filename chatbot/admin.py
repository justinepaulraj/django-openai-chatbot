from django.contrib import admin
from .models import Conversation, Message, Document

admin.site.register(Document)
admin.site.register(Conversation)
admin.site.register(Message)