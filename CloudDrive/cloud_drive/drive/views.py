from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
# drive/views.py
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings  # settings pour récupérer le dossier de base des médias
from .forms import FileUploadForm, FolderCreationForm, UserRegisterForm
from .models import Folder, File
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.views.decorators.http import require_POST
from django.db.models import Sum
from .forms import UserRegisterForm


# Vue pour la page d'accueil
def home(request):
    return render(request, 'drive/home.html')  # Assurez-vous de créer un template home.html

def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Chemin du dossier utilisateur
            user_folder = os.path.join(settings.MEDIA_ROOT, 'users', user.username)
            os.makedirs(user_folder, exist_ok=True)  # Créer le dossier si inexistant
            messages.success(request, f'Compte créé pour {user.username} ! Vous pouvez vous connecter.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'drive/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirection vers le tableau de bord
        else:
            messages.error(request, 'Nom d’utilisateur ou mot de passe incorrect.')
    return render(request, 'drive/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('login')

@login_required
def dashboard(request):
    # Calcul de la taille totale utilisée par l'utilisateur
    total_size = sum(f.file_size for f in File.objects.filter(user=request.user) if f.file_size)
    
    # Convertir en Mo pour l'affichage
    total_size_mb = total_size / (1024 * 1024)

    # Contexte pour le template
    context = {
        'total_size_mb': round(total_size_mb, 2),  # Arrondi à 2 décimales pour une meilleure lisibilité
    }
    
    return render(request, 'drive/dashboard.html', context)

@login_required
def account_stats(request):
    # Calcul de l'espace total utilisé
    total_storage = File.objects.filter(user=request.user).aggregate(total_size=Sum('file_size'))['total_size'] or 0
    
    # Calcul de l'espace utilisé par chaque format
    format_distribution = (
        File.objects.filter(user=request.user)
        .values('file_type')
        .annotate(total_size=Sum('file_size'))
        .order_by('-total_size')
    )

    # Préparer les données pour le graphique
    labels = []
    data = []
    percentages = []

    for entry in format_distribution:
        file_type = entry['file_type']
        total_size = entry['total_size'] or 0  # Défaut à 0 si None
        labels.append(file_type)
        data.append(total_size)
        
        # Calcul du pourcentage de l'espace total
        percentage = (total_size / total_storage * 100) if total_storage > 0 else 0
        percentages.append(percentage)

    chart_data = {
        'labels': labels,
        'data': data,
        'percentages': percentages,
    }

    return render(request, 'drive/account_stats.html', {
        'total_storage': total_storage,
        'format_distribution': format_distribution,
        'chart_data': chart_data,
    })


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            
            # Vérification de la taille du fichier (40 Mo maximum)
            if uploaded_file.size > 40 * 1024 * 1024:  # 40 Mo en octets
                messages.error(request, "La taille du fichier ne doit pas dépasser 40 Mo.")
                return redirect('upload')  # Redirection vers la page de téléversement

            # Récupération du dossier utilisateur
            user_folder = os.path.join(settings.MEDIA_ROOT, request.user.username)
            
            # Calcul du stockage total utilisé
            total_size = sum(f.file_size for f in File.objects.filter(user=request.user) if f.file_size)

            # Vérification de la limite de stockage total (100 Mo maximum)
            if total_size + uploaded_file.size > 100 * 1024 * 1024:  # 100 Mo en octets
                messages.error(request, "La limite de stockage de 100 Mo a été dépassée.")
                return redirect('upload')  # Redirection vers la page de téléversement

            # Si tout est valide, on sauvegarde le fichier
            file_instance = form.save(commit=False)
            file_instance.file_size = uploaded_file.size  # Taille du fichier en octets
            file_instance.file_type = uploaded_file.content_type  # Type MIME du fichier
            file_instance.user = request.user
            file_instance.save()  # Enregistre l'instance de fichier dans la base de données

            # Sauvegarde du fichier sur le système de fichiers
            fs = FileSystemStorage(location=user_folder)
            fs.save(uploaded_file.name, uploaded_file)

            messages.success(request, 'Fichier téléversé avec succès.')
            return redirect('dashboard')  # Redirection vers le tableau de bord

    else:
        form = FileUploadForm()  # Création d'une instance vide du formulaire pour les requêtes GET

    return render(request, 'drive/upload.html', {'form': form})


@login_required
def browse_files(request, folder_id=None):
    # Obtenir le dossier racine ou le dossier actuel sélectionné
    if folder_id:
        current_folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    else:
        current_folder = None

    # Récupérer les sous-dossiers et fichiers dans le dossier actuel
    folders = Folder.objects.filter(parent_folder=current_folder, user=request.user)
    files = File.objects.filter(folder=current_folder, user=request.user)

    context = {
        'current_folder': current_folder,
        'folders': folders,
        'files': files,
    }
    return render(request, 'drive/browse_files.html', context)

@login_required
def file_details(request, file_id):
    # Récupérer le fichier spécifique
    file = get_object_or_404(File, id=file_id, user=request.user)

    # Détecter le type de fichier pour la prévisualisation
    preview_url = None
    if file.file_type.startswith('image/'):
        preview_url = file.file.url  # Si c'est une image, on peut afficher directement l'URL du fichier
    elif file.file_type.startswith('video/'):
        preview_url = file.file.url  # Pour les vidéos, on pourrait utiliser un lecteur vidéo
    elif file.file_type == 'application/pdf':
        preview_url = file.file.url  # Pour les PDF, on peut également l'afficher directement

    # Passer les détails du fichier au template
    return render(request, 'drive/file_details.html', {
        'file': file,
        'preview_url': preview_url,  # Passer l'URL pour la prévisualisation
    })

@login_required
def create_folder(request):
    if request.method == 'POST':
        form = FolderCreationForm(request.POST)
        if form.is_valid():
            folder_instance = form.save(commit=False)
            folder_instance.user = request.user  # Associe le dossier à l'utilisateur connecté
            folder_instance.save()
            messages.success(request, 'Dossier créé avec succès.')
            return redirect('browse_files')  # Redirige vers la page de navigation des fichiers et dossiers
    else:
        form = FolderCreationForm()
    
    return render(request, 'drive/create_folder.html', {'form': form})

@login_required
def move_file(request, file_id, folder_id):
    # Obtenez le fichier à déplacer
    file = get_object_or_404(File, id=file_id, user=request.user)

    # Récupérez l'ID du dossier cible depuis les paramètres de requête
    target_folder_id = request.GET.get('target_folder_id')

    
    # Vérifiez si le dossier cible est la racine (None) ou un dossier spécifique
    target_folder = None if target_folder_id == '' else get_object_or_404(Folder, id=target_folder_id, user=request.user)

    # Met à jour le dossier du fichier
    file.folder = target_folder
    file.save()

    # Redirection vers le dossier cible ou la racine
    if target_folder:
        return redirect('browse_folder', folder_id=target_folder.id)
    else:
        return redirect('browse_files')  # Redirige vers la racine si aucun dossier cible

@login_required
@require_POST
def move_folder(request, folder_id, current_folder_id):
    # Récupérer `target_folder_id` depuis request.POST
    target_folder_id = request.POST.get('target_folder_id')

    if not target_folder_id:
        messages.error(request, "Veuillez sélectionner un dossier cible.")
        return redirect('browse_folder', folder_id=current_folder_id)

    try:
        folder = get_object_or_404(Folder, id=folder_id, user=request.user)
        target_folder = get_object_or_404(Folder, id=target_folder_id, user=request.user)

        # Vérification pour éviter les boucles
        if target_folder == folder :
            messages.error(request, "Vous ne pouvez pas déplacer un dossier dans lui-même ou dans un de ses sous-dossiers.")
            return redirect('browse_folder', folder_id=current_folder_id)

        # Déplacement du dossier
        folder.parent_folder = target_folder
        folder.save()
        messages.success(request, f"Le dossier '{folder.name}' a été déplacé avec succès.")
    except Folder.DoesNotExist:
        messages.error(request, "Dossier introuvable.")

    return redirect('browse_folder', folder_id=current_folder_id)

@login_required
def copy_file(request, file_id, current_folder_id):
    try:
        # Récupérer le fichier à copier et le dossier cible
        file = get_object_or_404(File, id=file_id, user=request.user)
        target_folder = Folder.objects.get(id=current_folder_id, user=request.user) if current_folder_id != 0 else None

        # Calculer la taille totale de stockage actuelle de l'utilisateur
        total_storage = File.objects.filter(user=request.user).aggregate(total_size=Sum('file_size'))['total_size'] or 0
        
        # Vérifier si la copie ferait dépasser la limite de 100 Mo
        if total_storage + file.file_size > 100 * 1024 * 1024:
            messages.error(request, "Impossible de copier ce fichier. La limite de stockage de 100 Mo serait dépassée.")
            # Redirection vers l'emplacement approprié
            return redirect('browse_folder', folder_id=current_folder_id) if current_folder_id != 0 else redirect('browse_files')

        # Copier le fichier si la limite n'est pas atteinte
        copied_file = File.objects.create(
            file=file.file,  # Ceci conserve le chemin du fichier existant
            user=file.user,
            folder=target_folder,
            file_size=file.file_size,
            file_type=file.file_type
        )

        messages.success(request, f"Fichier '{file.file.name}' copié avec succès.")
        
        # Redirection en fonction de la présence d'un dossier courant
        return redirect('browse_folder', folder_id=current_folder_id) if current_folder_id != 0 else redirect('browse_files')

    except File.DoesNotExist:
        messages.error(request, "Fichier introuvable.")
        return redirect('browse_files')
    except Folder.DoesNotExist:
        messages.error(request, "Dossier cible introuvable.")
        return redirect('browse_files')


@login_required
@transaction.atomic  # Pour assurer une copie complète ou aucun changement
def copy_folder(request, folder_id, current_folder_id):
    try:
        original_folder = get_object_or_404(Folder, id=folder_id, user=request.user)
        target_folder = Folder.objects.get(id=current_folder_id, user=request.user) if current_folder_id != 0 else None

        # Calculer la taille totale de stockage actuelle de l'utilisateur
        total_storage = File.objects.filter(user=request.user).aggregate(total_size=Sum('file_size'))['total_size'] or 0

        # Calculer la taille totale des fichiers dans le dossier à copier, y compris les sous-dossiers
        def calculate_total_folder_size(folder):
            total_size = folder.files.aggregate(size=Sum('file_size'))['size'] or 0
            for subfolder in folder.subfolders.all():
                total_size += calculate_total_folder_size(subfolder)
            return total_size

        folder_size_to_copy = calculate_total_folder_size(original_folder)

        # Vérifier si la copie ferait dépasser la limite de 100 Mo
        if total_storage + folder_size_to_copy > 100 * 1024 * 1024:
            # Calculer l'espace restant en Mo
            remaining_space = 100 * 1024 * 1024 - total_storage
            messages.error(request, f"Impossible de copier ce dossier. Espace insuffisant : il vous reste {remaining_space // (1024 * 1024)} Mo sur 100 Mo.")
            return redirect('browse_folder', folder_id=current_folder_id) if current_folder_id != 0 else redirect('browse_files')

        # Copie du dossier principal
        copied_folder = Folder.objects.create(
            name=f"{original_folder.name} - Copie",
            user=request.user,
            parent_folder=target_folder
        )

        # Fonction récursive pour copier les sous-dossiers et les fichiers
        def copy_contents(source_folder, dest_folder):
            # Copier les fichiers du dossier source
            for file in source_folder.files.all():
                File.objects.create(
                    file=file.file,
                    user=file.user,
                    folder=dest_folder,
                    file_size=file.file_size,
                    file_type=file.file_type
                )

            # Copier les sous-dossiers du dossier source
            for subfolder in source_folder.subfolders.all():
                copied_subfolder = Folder.objects.create(
                    name=subfolder.name,
                    user=request.user,
                    parent_folder=dest_folder
                )
                copy_contents(subfolder, copied_subfolder)

        # Copier le contenu du dossier original dans le nouveau dossier
        copy_contents(original_folder, copied_folder)

        messages.success(request, f"Dossier '{original_folder.name}' copié avec succès.")
        
        # Rediriger en fonction de la présence d'un dossier courant
        return redirect('browse_folder', folder_id=current_folder_id) if current_folder_id != 0 else redirect('browse_files')

    except Folder.DoesNotExist:
        messages.error(request, "Dossier ou dossier cible introuvable.")
        return redirect('browse_files')


@login_required
def delete_file(request, file_id):
    file_instance = get_object_or_404(File, id=file_id, user=request.user)
    parent_folder = file_instance.folder  # Stocker le dossier parent avant suppression
    file_instance.delete()  # Supprimer le fichier

    messages.success(request, 'Fichier supprimé avec succès.')

    # Rediriger vers le dossier parent s'il existe, sinon vers la racine
    if parent_folder:
        return redirect('browse_folder', folder_id=parent_folder.id)
    else:
        return redirect('browse_files')  # Redirection vers la racine si aucun dossier parent

@login_required
def delete_folder(request, folder_id):
    folder_instance = get_object_or_404(Folder, id=folder_id, user=request.user)
    parent_folder = folder_instance.parent_folder  # Stocker le dossier parent avant suppression
    folder_instance.delete()  # Supprimer le dossier

    messages.success(request, 'Dossier supprimé avec succès.')

    # Rediriger vers le dossier parent si présent, sinon vers la racine des dossiers
    if parent_folder:
        return redirect('browse_folder', folder_id=parent_folder.id)
    else:
        return redirect('browse_files')  # Rediriger vers la racine si aucun dossier parent

