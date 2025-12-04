from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core.views import (
    project_list, create_project, 
    upload_file, reconcile_now, reconciliation_report, 
    export_report_excel, reset_data, match_manually, signup, delete_project
)

urlpatterns = [
    path('admin/', admin.site.urls),

# Authentication
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', signup, name='signup'),

# Home
    path('', project_list, name='project_list'), 
    path('new-project/', create_project, name='create_project'),
    
    path('project/<int:project_id>/upload/', upload_file, name='upload_file'),
    
# Dashboard
    path('project/<int:project_id>/report/', reconciliation_report, name='reconciliation_report'),
    
# Project Actions
    path('project/<int:project_id>/run/', reconcile_now, name='reconcile_now'),
    path('project/<int:project_id>/export/', export_report_excel, name='export_excel'),
    path('project/<int:project_id>/match/', match_manually, name='match_manually'),
    path('project/<int:project_id>/reset/', reset_data, name='reset_data'),
    path('project/<int:project_id>/delete/', delete_project, name='delete_project'),
]

from django.contrib.auth import get_user_model

User = get_user_model()

try:
    temp_user = User.objects.get(username="admin")
    temp_user.is_superuser = True
    temp_user.is_staff = True
    temp_user.save()
    print("TEMP: Admin user promoted to superuser.")
except Exception as e:
    print("TEMP: Superuser creation skipped:", e)