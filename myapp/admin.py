from django.contrib import admin
from .models import User,Post,Report,Comment,Friendship,Messages
# Register your models here.

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Report)
admin.site.register(Comment)
admin.site.register(Friendship)
admin.site.register(Messages)