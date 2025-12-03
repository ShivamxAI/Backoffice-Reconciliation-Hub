import pandas as pd
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth import login 
from django.contrib.auth.decorators import login_required 

from .forms import UploadFileForm, ProjectForm 
from .models import Transaction, StatementFile, Project 

# Authentication of user
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('project_list') 
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {'form': form})

# Project Management
@login_required
def project_list(request):
    """ The New Homepage: Lists projects & Button to create new """
    projects = Project.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/project_list.html', {'projects': projects})

@login_required
def create_project(request):
    """ Handles project creation """
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user 
            project.save()
            messages.success(request, f"Project '{project.name}' created!")
            return redirect('upload_file', project_id=project.id) 
    else:
        form = ProjectForm()
    return render(request, 'core/create_project.html', {'form': form})

# File uploading
@login_required
def upload_file(request, project_id): 
    project = get_object_or_404(Project, id=project_id, user=request.user) 
    
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            statement_file = form.save(commit=False)
            statement_file.project = project 
            statement_file.save()
            
            try:
                if statement_file.file.name.endswith('.csv'):
                    df = pd.read_csv(statement_file.file.path)
                else:
                    df = pd.read_excel(statement_file.file.path)
                
                df.columns = df.columns.str.strip().str.lower()

                transactions_list = []
                for index, row in df.iterrows():
                    transactions_list.append(Transaction(
                        statement_file=statement_file,
                        date=pd.to_datetime(row.get('date')).date(),
                        description=row.get('description'),
                        reference=row.get('reference', ''),
                        amount=row.get('amount'),
                        is_reconciled=False
                    ))
                
                Transaction.objects.bulk_create(transactions_list)
                
                messages.success(request, f"Uploaded to {project.name}!")
                return redirect('reconciliation_report', project_id=project.id)

            except Exception as e:
                statement_file.delete()
                print(f"❌ UPLOAD ERROR: {e}")
                messages.error(request, f"Error processing file: {str(e)}")

    else:
        form = UploadFileForm()

    return render(request, 'core/upload.html', {'form': form, 'project': project}) 

# Auto-Reconciliation
@login_required
def reconcile_now(request, project_id): 
    project = get_object_or_404(Project, id=project_id, user=request.user)

    bank_transactions = Transaction.objects.filter(
        statement_file__project=project, 
        statement_file__file_type='bank', 
        is_reconciled=False
    )
    
    ledger_transactions = Transaction.objects.filter(
        statement_file__project=project, 
        statement_file__file_type='ledger', 
        is_reconciled=False
    )

    matches_found = 0

    for bank_txn in bank_transactions:
        match = ledger_transactions.filter(amount=bank_txn.amount).first()

        if match:
            bank_txn.is_reconciled = True
            bank_txn.reconciliation_method = 'auto' 
            bank_txn.save()

            match.is_reconciled = True
            match.reconciliation_method = 'auto' 
            match.save()

            ledger_transactions = ledger_transactions.exclude(id=match.id)
            matches_found += 1

    if matches_found > 0:
        messages.success(request, f"Reconciliation Complete! {matches_found} pairs matched.")
    else:
        messages.info(request, "No new matches found.")

    return redirect('reconciliation_report', project_id=project.id) 

# Reconcilation report view
@login_required
def reconciliation_report(request, project_id): 
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    bank_breaks = Transaction.objects.filter(
        statement_file__project=project, 
        statement_file__file_type='bank', 
        is_reconciled=False
    )
    
    ledger_breaks = Transaction.objects.filter(
        statement_file__project=project, 
        statement_file__file_type='ledger', 
        is_reconciled=False
    )

    reconciled_txns = Transaction.objects.filter(
        statement_file__project=project, 
        is_reconciled=True
    ).order_by('-date')

    context = {
        'project': project, 
        'bank_breaks': bank_breaks,
        'ledger_breaks': ledger_breaks,
        'reconciled_txns': reconciled_txns,
    }
    
    return render(request, 'core/report.html', context)

# Exporting data in Excel
@login_required
def export_report_excel(request, project_id): 
    project = get_object_or_404(Project, id=project_id, user=request.user)

    all_transactions = Transaction.objects.filter(
        statement_file__project=project 
    ).select_related('statement_file').order_by('date')

    data_list = []
    for txn in all_transactions:
        if txn.is_reconciled:
            if txn.reconciliation_method == 'manual':
                status_label = "Manually Reconciled"
            else:
                status_label = "Auto Reconciled"
        else:
            status_label = "Unreconciled"

        source_label = txn.statement_file.get_file_type_display()

        data_list.append({
            'Date': txn.date,
            'Source': source_label,
            'Description': txn.description,
            'Reference': txn.reference,
            'Amount': float(txn.amount),
            'Status': status_label
        })

    df_master = pd.DataFrame(data_list)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{project.name}_Reconciliation_Report.xlsx"' 

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        if not df_master.empty:
            df_master.to_excel(writer, sheet_name='All Transactions', index=False)
            if not df_master.empty:
                summary = df_master.groupby(['Source', 'Status'])['Amount'].sum().reset_index()
                summary.to_excel(writer, sheet_name='Summary Pivot', index=False)
        else:
            pd.DataFrame({'Info': ['No transactions found']}).to_excel(writer, sheet_name='All Transactions')

    return response

# Manually matching the data
@login_required
def match_manually(request, project_id): 
    if request.method == 'POST':
        bank_ids = request.POST.getlist('bank_ids')
        ledger_ids = request.POST.getlist('ledger_ids')

        bank_txns = Transaction.objects.filter(id__in=bank_ids)
        ledger_txns = Transaction.objects.filter(id__in=ledger_ids)

        bank_sum = sum([t.amount for t in bank_txns], Decimal(0))
        ledger_sum = sum([t.amount for t in ledger_txns], Decimal(0))

        diff = bank_sum - ledger_sum

        if diff == 0:
            bank_txns.update(is_reconciled=True, reconciliation_method='manual')
            ledger_txns.update(is_reconciled=True, reconciliation_method='manual')
            messages.success(request, f"Manual Match Successful! Reconciled ${bank_sum}")
        else:
            messages.error(request, f"Sums do not match! Bank: {bank_sum} vs Ledger: {ledger_sum} (Diff: {diff})")

    return redirect('reconciliation_report', project_id=project_id) 

# Resetting the data
@login_required
def reset_data(request, project_id): 
    project = get_object_or_404(Project, id=project_id, user=request.user)

    if request.method == 'POST':
        count = StatementFile.objects.filter(project=project).count()
        StatementFile.objects.filter(project=project).delete()
        messages.warning(request, f"Reset project '{project.name}'. Deleted {count} files and all associated transactions.")
        
        return redirect('upload_file', project_id=project.id) 
    
    return redirect('upload_file', project_id=project.id)

# Deleting a project
@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    if request.method == 'POST':
        project_name = project.name
        project.delete() 
        messages.success(request, f"Project '{project_name}' has been deleted.")
        return redirect('project_list')
    
    return redirect('project_list')