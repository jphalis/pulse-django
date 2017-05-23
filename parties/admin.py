from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Party

# Register your models here.


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'is_active',)
    list_display_links = ('id', 'name',)
    list_filter = ('created', 'modified', 'is_active',)
    raw_id_fields = ['user', 'attendees', 'requesters', 'invited_users',
                     'likers']
    fieldsets = (
        (None,
            {'fields': ('id', 'party_type', 'invite_type', 'name', 'location',
                        'latitude', 'longitude', 'party_size', 'party_month',
                        'party_day', 'party_year', 'start_time', 'end_time',
                        'description', 'image', 'user', 'attendees',
                        'requesters', 'invited_users', 'likers',
                        'recurrence',)}),
        (_('Permissions'),
            {'fields': ('is_active',)}),
        (_('Dates'),
            {'fields': ('created', 'modified',)}),
    )
    readonly_fields = ('id', 'created', 'modified',)
    search_fields = ('name', 'user__full_name',)
    actions = ('enable', 'disable',)

    def enable(self, request, queryset):
        """Updates is_active to be True."""
        queryset.update(is_active=True)
    enable.short_description = _("Enable selected parties")

    def disable(self, request, queryset):
        """Updates is_active to be False."""
        queryset.update(is_active=False)
    disable.short_description = _("Disable selected parties")

    class Meta:
        model = Party
