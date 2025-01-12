from django.shortcuts import render

def index(request):
    return render(request, 'main/index.html')

def general_statistics(request):
    return render(request, 'main/general_statistics.html')

def demand(request):
    return render(request, 'main/demand.html')

def geography(request):
    return render(request, 'main/geography.html')

def skills(request):
    return render(request, 'main/skills.html')

def latest_vacancies(request):
    return render(request, 'main/latest_vacancies.html')
