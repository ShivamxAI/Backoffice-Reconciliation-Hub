from django.contrib import admin
from .models import StatementFile, Transaction

admin.site.register(StatementFile)
admin.site.register(Transaction)
