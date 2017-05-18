from django.contrib import admin

from .models import Feed

# Register your models here.


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']
    list_display_links = ('id',)
    readonly_fields = ['created', 'modified']

    class Meta:
        model = Feed
