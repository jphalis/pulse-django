from django.contrib import admin
from django.core.urlresolvers import reverse

from flag.models import Flag


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'link_to_party', 'resolved', 'flag_count')
    list_filter = ('flag_count', 'resolved',)
    search_fields = ['id', 'creator']
    fields = ('id', 'creator', 'party', 'comment', 'resolved', 'flag_count',
              'created', 'modified',)
    readonly_fields = ['id', 'flag_count', 'created', 'modified']
    ordering = ['resolved']

    class Meta:
        model = Flag

    def link_to_party(self, obj):
        link = reverse("admin:parties_party_change", args=[obj.party.id])
        return u'<a href="{}">{}</a>'.format(link, obj.party.pk)
    link_to_party.allow_tags = True
