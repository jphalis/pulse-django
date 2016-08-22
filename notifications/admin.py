from django.contrib import admin

from .models import Notification

# Register your models here.


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient', '__str__', 'read']
    list_display_links = ('id', 'recipient',)
    list_filter = ['read']
    readonly_fields = ['created', 'modified']

    class Meta:
        model = Notification


admin.site.register(Notification, NotificationAdmin)
