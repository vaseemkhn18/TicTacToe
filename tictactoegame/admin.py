from django.contrib import admin
from .models import session, connection, status
# Register your models here.
admin.site.register(session)
admin.site.register(connection)
admin.site.register(status)