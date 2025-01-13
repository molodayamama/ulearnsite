import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from django.conf import settings

class DataProcessor:
    def __init__(self, csv_path):
        # Читаем CSV с правильными названиями колонок
        self.df = pd.read_csv(
            csv_path,
            names=[
                'name', 'key_skills', 'salary_from', 'salary_to',
                'salary_currency', 'area_name', 'published_at'
            ],
            low_memory=False
        )

    # Преобразуем даты в datetime более надежным способом
        def parse_date(date_str):
            try:
                date_str = date_str.split('+')[0]
                return pd.to_datetime(date_str)
            except:
                return None

        # Применяем функцию parse_date к колонке published_at
        self.df['published_at'] = self.df['published_at'].apply(parse_date)
        self.df['year'] = self.df['published_at'].dt.year

        # Преобразуем зарплаты в числовой формат для основного DataFrame
        self.df['salary_from'] = pd.to_numeric(self.df['salary_from'], errors='coerce')
        self.df['salary_to'] = pd.to_numeric(self.df['salary_to'], errors='coerce')

        # Создаем PHP DataFrame правильным способом
        mask = self.df['name'].str.contains('php|пхп|рнр', case=False, na=False)
        self.php_df = self.df[mask].copy()  # Используем .copy() для создания независимой копии



    def convert_salary_to_rub(self, row):
        """Конвертация зарплаты в рубли"""
        if pd.isna(row['salary_from']) and pd.isna(row['salary_to']):
            return None

        salary_from = row['salary_from'] if not pd.isna(row['salary_from']) else 0
        salary_to = row['salary_to'] if not pd.isna(row['salary_to']) else salary_from

        if salary_from == 0 and salary_to == 0:
            return None

        avg_salary = (salary_from + salary_to) / 2 if salary_to != 0 else salary_from

        # Курсы валют по годам
        currency_rates = {
            2005: {'USD': 28.5, 'EUR': 34.2, 'RUR': 1, 'RUB': 1},
            2006: {'USD': 26.3, 'EUR': 34.7, 'RUR': 1, 'RUB': 1},
            # Добавьте курсы для остальных лет
            2024: {'USD': 90, 'EUR': 98, 'RUR': 1, 'RUB': 1}
        }

        year = row['year']
        if year not in currency_rates:
            year = 2024

        currency = row['salary_currency']
        if pd.isna(currency) or currency not in currency_rates[year]:
            return None

        return avg_salary * currency_rates[year][currency]

    def process_salary_statistics(self):
        """Обработка статистики зарплат для всех вакансий и PHP"""
        # Для всех вакансий
        self.df['salary_rub'] = self.df.apply(self.convert_salary_to_rub, axis=1)
        self.df = self.df[self.df['salary_rub'] < 10000000]  # Убираем выбросы

        all_salary_by_year = self.df.groupby('year')['salary_rub'].mean().round(2)
        all_count_by_year = self.df.groupby('year').size()

        # Для PHP вакансий
        self.php_df['salary_rub'] = self.php_df.apply(self.convert_salary_to_rub, axis=1)
        self.php_df = self.php_df[self.php_df['salary_rub'] < 10000000]

        php_salary_by_year = self.php_df.groupby('year')['salary_rub'].mean().round(2)
        php_count_by_year = self.php_df.groupby('year').size()

        return (all_salary_by_year, all_count_by_year,
                php_salary_by_year, php_count_by_year)

    def process_geography_data(self):
        """Обработка географических данных для всех вакансий и PHP"""
        # Для всех вакансий
        total_vacancies = len(self.df)
        city_stats = self.df.groupby('area_name').agg({
            'salary_rub': 'mean',
            'name': 'count'
        }).round(2)
        city_stats['vacancy_share'] = (city_stats['name'] / total_vacancies * 100).round(2)
        all_city_stats = city_stats[city_stats['vacancy_share'] > 1]

        # Для PHP вакансий
        total_php_vacancies = len(self.php_df)
        php_city_stats = self.php_df.groupby('area_name').agg({
            'salary_rub': 'mean',
            'name': 'count'
        }).round(2)
        php_city_stats['vacancy_share'] = (php_city_stats['name'] / total_php_vacancies * 100).round(2)
        php_city_stats = php_city_stats[php_city_stats['vacancy_share'] > 1]

        return all_city_stats, php_city_stats

    def process_skills(self):
        """Обработка навыков для всех вакансий и PHP"""
        # Для всех вакансий
        all_skills_df = self.df[self.df['key_skills'].notna()]
        all_skills = []
        for skills in all_skills_df['key_skills']:
            if isinstance(skills, str):
                all_skills.extend([skill.strip() for skill in skills.split('\n')])
        all_skills_count = pd.Series(all_skills).value_counts()

        # Для PHP вакансий
        php_skills_df = self.php_df[self.php_df['key_skills'].notna()]
        php_skills = []
        for skills in php_skills_df['key_skills']:
            if isinstance(skills, str):
                php_skills.extend([skill.strip() for skill in skills.split('\n')])
        php_skills_count = pd.Series(php_skills).value_counts()

        return all_skills_count, php_skills_count

    def create_salary_graph(self, data, title, filename, is_general=True):
        """Создание графика зарплат"""
        plt.figure(figsize=(12, 6))
        plt.plot(data.index, data.values, marker='o')
        plt.title(title)
        plt.xlabel('Год')
        plt.ylabel('Средняя зарплата (руб.)')
        plt.grid(True)
        plt.xticks(rotation=45)

        graph_path = os.path.join(settings.MEDIA_ROOT, 'graphs', filename)
        os.makedirs(os.path.dirname(graph_path), exist_ok=True)
        plt.savefig(graph_path, bbox_inches='tight', dpi=300)
        plt.close()
        return f'graphs/{filename}'

    def create_count_graph(self, data, title, filename, is_general=True):
        """Создание графика количества вакансий"""
        plt.figure(figsize=(12, 6))
        plt.plot(data.index, data.values, marker='o')
        plt.title(title)
        plt.xlabel('Год')
        plt.ylabel('Количество вакансий')
        plt.grid(True)
        plt.xticks(rotation=45)

        graph_path = os.path.join(settings.MEDIA_ROOT, 'graphs', filename)
        os.makedirs(os.path.dirname(graph_path), exist_ok=True)
        plt.savefig(graph_path, bbox_inches='tight', dpi=300)
        plt.close()
        return f'graphs/{filename}'

    def create_geography_graph(self, data, title, filename, is_general=True):
        """Создание графика географии"""
        plt.figure(figsize=(12, 8))
        top_10_cities = data.head(10)

        plt.pie(
            top_10_cities['vacancy_share'],
            labels=top_10_cities.index,
            autopct='%1.1f%%',
            startangle=90
        )
        plt.title(title)

        graph_path = os.path.join(settings.MEDIA_ROOT, 'graphs', filename)
        os.makedirs(os.path.dirname(graph_path), exist_ok=True)
        plt.savefig(graph_path, bbox_inches='tight', dpi=300)
        plt.close()
        return f'graphs/{filename}'

    def create_skills_graph(self, data, title, filename, is_general=True):
        """Создание графика навыков"""
        plt.figure(figsize=(15, 8))
        data.head(20).plot(kind='bar')
        plt.title(title)
        plt.xlabel('Навыки')
        plt.ylabel('Количество упоминаний')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        graph_path = os.path.join(settings.MEDIA_ROOT, 'graphs', filename)
        os.makedirs(os.path.dirname(graph_path), exist_ok=True)
        plt.savefig(graph_path, bbox_inches='tight', dpi=300)
        plt.close()
        return f'graphs/{filename}'
