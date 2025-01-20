from django.shortcuts import render
from django.core.cache import cache
from .models import MainPage, SalaryStatistics, GeographyData, Skill, Graph
import requests
from datetime import datetime

def index(request):
    """Представление главной страницы"""
    main_info = MainPage.objects.first()
    if not main_info:
        main_info = MainPage.objects.create(
            title="PHP-программист",
            description="пук-пук-пук-пук",
            image="/media/profession_images/default.jpg"
        )

    context = {
        'main_info': main_info
    }
    return render(request, 'main/index.html', context)


def general_statistics(request):
    """Представление общей статистики"""
    context = {
        # Статистика зарплат
        'salary_statistics': SalaryStatistics.objects.filter(
            is_general=True
        ).order_by('year'),
        'salary_graphs': Graph.objects.filter(
            graph_type='salary',
            is_general=True
        ),

        # Статистика количества вакансий
        'vacancy_count_statistics': SalaryStatistics.objects.filter(
            is_general=True
        ).order_by('year'),
        'demand_graphs': Graph.objects.filter(
            graph_type='demand',
            is_general=True
        ),

        # Статистика по городам (зарплаты)
        'city_salary_statistics': GeographyData.objects.filter(
            is_general=True
        ).order_by('-average_salary'),
        'geography_salary_graphs': Graph.objects.filter(
            graph_type='geography_salary',
            is_general=True
        ),

        # Статистика по городам (доли)
        'city_share_statistics': GeographyData.objects.filter(
            is_general=True
        ).order_by('-vacancy_share'),
        'geography_share_graphs': Graph.objects.filter(
            graph_type='geography_share',
            is_general=True
        ),

        # Статистика навыков
        'skills_statistics': Skill.objects.filter(
            is_general=True
        ).order_by('-count')[:20],
        'skills_graphs': Graph.objects.filter(
            graph_type='skills',
            is_general=True
        ),
    }
    return render(request, 'main/general_statistics.html', context)

def demand(request):
    """Представление востребованности (PHP)"""
    context = {
        'php_salary_statistics': SalaryStatistics.objects.filter(
            is_general=False
        ).order_by('year'),
        'php_salary_graphs': Graph.objects.filter(
            graph_type='salary',
            is_general=False
        ),
        'php_vacancy_statistics': SalaryStatistics.objects.filter(
            is_general=False
        ).order_by('year'),
        'php_demand_graphs': Graph.objects.filter(
            graph_type='demand',
            is_general=False
        ),
    }
    return render(request, 'main/demand.html', context)

def geography(request):
    """Представление географии (PHP)"""
    context = {
        'php_city_salary_statistics': GeographyData.objects.filter(
            is_general=False
        ).order_by('-average_salary'),
        'php_city_share_statistics': GeographyData.objects.filter(
            is_general=False
        ).order_by('-vacancy_share'),
        'php_salary_city_graphs': Graph.objects.filter(
            graph_type='geography_salary',
            is_general=False
        ),
        'php_geography_graphs': Graph.objects.filter(
            graph_type='geography_share',
            is_general=False
        ),
    }
    return render(request, 'main/geography.html', context)

def skills(request):
    """Представление навыков (PHP)"""
    all_php_skills = Skill.objects.filter(is_general=False)
    total_mentions = sum(skill.count for skill in all_php_skills)

    skills_with_percentage = []
    for skill in all_php_skills.order_by('-count')[:20]:
        percentage = (skill.count / total_mentions * 100) if total_mentions > 0 else 0
        skills_with_percentage.append({
            'name': skill.name,
            'count': skill.count,
            'percentage': percentage
        })

    context = {
        'php_skills_statistics': skills_with_percentage,
        'php_skills_graphs': Graph.objects.filter(
            graph_type='skills',
            is_general=False
        ),
    }
    return render(request, 'main/skills.html', context)

def latest_vacancies(request):
    """Представление последних вакансий"""
    # Кэшированные вакансии
    vacancies = cache.get('latest_php_vacancies')

    if vacancies is None:
        try:
            params = {
                'text': 'PHP OR ПХП OR РНР',
                'period': 1,
                'per_page': 10,
                'order_by': 'publication_time',
            }

            response = requests.get('https://api.hh.ru/vacancies', params=params)
            response.raise_for_status()

            data = response.json()
            vacancies = []

            # Обработка каждой вакансии
            for item in data['items']:
                vacancy = {
                    'title': item['name'],
                    'company': item['employer']['name'],
                    'region': item['area']['name'],
                    'published_at': datetime.strptime(
                        item['published_at'],
                        '%Y-%m-%dT%H:%M:%S%z'
                    ),
                    'skills': '',
                    'salary_from': None,
                    'salary_to': None,
                    'salary_currency': None,
                }

                if item['salary']:
                    vacancy['salary_from'] = item['salary']['from']
                    vacancy['salary_to'] = item['salary']['to']
                    vacancy['salary_currency'] = item['salary']['currency']

                # Дополнительный запрос для получения детальной информации
                try:
                    detailed_response = requests.get(f"https://api.hh.ru/vacancies/{item['id']}")
                    detailed_response.raise_for_status()
                    detailed_data = detailed_response.json()

                    if detailed_data.get('key_skills'):
                        skills = [skill['name'] for skill in detailed_data['key_skills']]
                        vacancy['skills'] = ', '.join(skills)

                    vacancy['description'] = detailed_data.get('description', '')

                except requests.RequestException:
                    pass

                vacancies.append(vacancy)

            # Кэшируем результат на 15 минут
            cache.set('latest_php_vacancies', vacancies, 900)

        except requests.RequestException:
            vacancies = []

    context = {
        'vacancies': vacancies
    }
    return render(request, 'main/latest_vacancies.html', context)
