from django.contrib import admin
from .models import User,Address,CartItem,Favorite

# Register your models here.
admin.site.register(User)
admin.site.register(Address)
admin.site.register(CartItem)
admin.site.register(Favorite)
