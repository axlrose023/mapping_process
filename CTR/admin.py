from django.contrib import admin
from .models import Provider, Company, Client, Session, SessionFileType, SessionCodesDeductions, SessionCodesMemos, \
    SessionCodesEarnings, SessionMappingEarnings, SessionMappingDeductions, SessionMappingMemos, SessionMappingTaxes, \
    SessionFileLink

admin.site.register(Provider)
admin.site.register(Company)
admin.site.register(Client)
admin.site.register(Session)
admin.site.register(SessionFileType)
admin.site.register(SessionCodesDeductions)
admin.site.register(SessionCodesMemos)
admin.site.register(SessionCodesEarnings)
admin.site.register(SessionMappingEarnings)
admin.site.register(SessionMappingDeductions)
admin.site.register(SessionMappingMemos)
admin.site.register(SessionMappingTaxes)
admin.site.register(SessionFileLink)
