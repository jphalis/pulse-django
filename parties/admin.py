from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Party

# Register your models here.


class PartyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'is_active',)
    list_display_links = ('id', 'name',)
    list_filter = ('created', 'modified', 'is_active',)
    raw_id_fields = ['user', 'attendees']
    fieldsets = (
        (None,
            {'fields': ('party_type', 'name', 'location', 'party_size',
                        'party_month', 'party_day', 'start_time', 'end_time',
                        'description', 'image', 'user', 'attendees',)}),
        (_('Permissions'),
            {'fields': ('is_active',)}),
        (_('Dates'),
            {'fields': ('created', 'modified',)}),
    )
    readonly_fields = ('created', 'modified',)
    search_fields = ('name', 'user__get_full_name',)

    class Meta:
        model = Party


admin.site.register(Party, PartyAdmin)
