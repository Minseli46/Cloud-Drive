from django.urls import path
from .views import signup, login_view, logout_view, home, dashboard, upload_file, browse_files, file_details, create_folder, move_file, move_folder, copy_file, delete_file, delete_folder, copy_folder, account_stats

urlpatterns = [
    path('', home, name='home'),  # Route pour la page d'accueil
    path('signup/', signup, name='signup'),  # Route pour l'inscription
    path('login/', login_view, name='login'),  # Route pour la connexion
    path('logout/', logout_view, name='logout'),  # Route pour la déconnexion
    path('dashboard/', dashboard, name='dashboard'),  # Nouveau chemin pour le dashboard
    path('upload/', upload_file, name='upload'),
    path('account-stats/', account_stats, name='account_stats'),
    path('browse/', browse_files, name='browse_files'),
    path('browse/<int:folder_id>/', browse_files, name='browse_folder'),
    path('file/<int:file_id>/', file_details, name='file_details'),
    path('create-folder/', create_folder, name='create_folder'),
    path('move-file/<int:file_id>/<int:folder_id>/', move_file, name='move_file'),
    path('move-folder/<int:folder_id>/<int:current_folder_id>/', move_folder, name='move_folder'),
    path('copy-file/<int:file_id>/<int:current_folder_id>/', copy_file, name='copy_file'),
    path('copy_folder/<int:folder_id>/<int:current_folder_id>/', copy_folder, name='copy_folder'),
    path('delete-file/<int:file_id>/', delete_file, name='delete_file'),
    path('delete-folder/<int:folder_id>/', delete_folder, name='delete_folder'),
]
