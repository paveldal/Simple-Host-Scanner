from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Profile, ScanResult
from .forms import ProfileForm
from .utils import collect_system_info
from django.contrib import messages
from django.http import JsonResponse

def index(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ProfileForm()
    
    profiles = Profile.objects.all()
    return render(request, 'HostReview/index.html', {'profiles': profiles, 'form': form})

def scan_system(request, profile_id):
    try:
        collect_system_info(profile_id)
        messages.success(request, "Сканирование началось.")
        # ... логика ...
    except Profile.DoesNotExist:
        messages.error(request, "Профиль не найден.")
    return redirect('index')

def ajax_scan_system(request):
    profile_id = request.GET.get('profile_id')
    if profile_id:
        try:
            # Здесь должна быть реализация запуска сканирования
            collect_system_info(profile_id)
            return JsonResponse({"success": True, "message": "Сканирование началось."})
        except Profile.DoesNotExist:
            return JsonResponse({"success": False, "message": "Профиль не найден."})
    return JsonResponse({"success": False, "message": "Не указан ID профиля."})

def ajax_check_scan_status(request):
    profile_id = request.GET.get('profile_id')
    if profile_id:
        try:
            # Это пример, вам нужно будет реализовать логику определения статуса сканирования
            # Например, вы можете проверить, есть ли недавно завершенные результаты сканирования в базе данных
            profile = Profile.objects.get(pk=profile_id)
            last_scan = profile.scan_results.last()
            print(last_scan)
            if last_scan.status == 'completed':  # Предположим, что у вас есть поле 'status' в модели ScanResult
                return JsonResponse({"status": "completed"})
            else:
                return JsonResponse({"status": "scanning"})
        except Profile.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Профиль не найден."})
    return JsonResponse({"status": "error", "message": "Не указан ID профиля."})

def scan_system(request, profile_id):
    try:
        collect_system_info(profile_id)
        return HttpResponse("Сканирование успешно запущено.")
    except Profile.DoesNotExist:
        return HttpResponse("Профиль не найден.", status=404)

def scan_results(request, profile_id):
    try:
        profile = Profile.objects.get(pk=profile_id)
        results = profile.scan_results.all().order_by('-timestamp') 
        return render(request, 'HostReview/scan_results.html', {'profile': profile, 'results': results})
    except Profile.DoesNotExist:
        return HttpResponse("Профиль не найден.", status=404)

def delete_profile(request, profile_id):
    try:
        profile = Profile.objects.get(pk=profile_id)
        profile.delete()
        return redirect('index')
    except Profile.DoesNotExist:
        return HttpResponse("Профиль не найден.", status=404)
