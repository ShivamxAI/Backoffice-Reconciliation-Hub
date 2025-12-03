from django.db import models
from django.contrib.auth.models import User

# Project Model
class Project(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Files Model
class StatementFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE) 
    
    file = models.FileField(upload_to='uploads/')
    file_type = models.CharField(max_length=10, choices=[('bank', 'Bank Statement'), ('ledger', 'Internal Ledger')])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name} - {self.file_type}"

# Transaction Model
class Transaction(models.Model):
    statement_file = models.ForeignKey(StatementFile, on_delete=models.CASCADE)

    date = models.DateField() 
    description = models.CharField(max_length=255)
    reference = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    is_reconciled = models.BooleanField(default=False)
    reconciliation_method = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.date} - {self.amount}"