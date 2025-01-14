import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from django.conf import settings
import numpy as np

class DataProcessor:
    def __init__(self, csv_path):
        # Читаем CSV с правильными названиями колонок
        self.df = pd.read_csv(
            csv_path,
            names=[
                'name', 'key_skills', 'salary_from', 'salary_to',
                'salary_currency', 'area_name', 'published_at'
            ],
            dtype={
                'name': str,
                'key_skills': str,
                # Убираем предварительное приведение типов для зарплат
                'salary_currency': str,
                'area_name': str,
                'published_at': str
            },
            na_values=[''],
            low_memory=False
        )

        # Оптимизированная обработка дат
        self.df['published_at'] = pd.to_datetime(
            self.df['published_at'].str.split('+').str[0],
            format='%Y-%m-%dT%H:%M:%S',
            errors='coerce'
        )
        self.df['year'] = self.df['published_at'].dt.year

        # Преобразование зарплат в числовой формат
        self.df['salary_from'] = pd.to_numeric(self.df['salary_from'], errors='coerce')
        self.df['salary_to'] = pd.to_numeric(self.df['salary_to'], errors='coerce')

        # Создание маски для PHP вакансий
        php_mask = self.df['name'].str.contains('php|пхп|рнр', case=False, na=False)
        self.php_df = self.df[php_mask].copy()

        # Подготовка данных для зарплат
        self._prepare_salary_data()


    def _prepare_salary_data(self):
        """Подготовка данных о зарплатах"""
        # Создаем словарь курсов валют (можно расширить)
        self.currency_rates = {
            'USD': 90, 'EUR': 98, 'RUR': 1, 'RUB': 1,
            'KZT': 0.15, 'BYR': 27, 'UAH': 2.5, 'GEL': 34
        }

        # Конвертация зарплат в рубли
        self.df['salary_rub'] = self.df.apply(self._convert_salary_to_rub, axis=1)
        self.php_df['salary_rub'] = self.php_df.apply(self._convert_salary_to_rub, axis=1)

        # Удаление выбросов
        salary_mask = self.df['salary_rub'] < 10000000
        self.df = self.df[salary_mask]
        self.php_df = self.php_df[self.php_df['salary_rub'] < 10000000]

    def _convert_salary_to_rub(self, row):
        """Оптимизированная конвертация зарплаты в рубли"""
        if pd.isna(row['salary_from']) and pd.isna(row['salary_to']):
            return None

        salary_from = row['salary_from'] if not pd.isna(row['salary_from']) else 0
        salary_to = row['salary_to'] if not pd.isna(row['salary_to']) else salary_from

        if salary_from == 0 and salary_to == 0:
            return None

        avg_salary = (salary_from + salary_to) / 2 if salary_to != 0 else salary_from
        currency = row['salary_currency']

        if pd.isna(currency) or currency not in self.currency_rates:
            return None

        return avg_salary * self.currency_rates[currency]

    def process_salary_statistics(self):
        """Оптимизированная обработка статистики зарплат"""
        # Группировка данных
        all_stats = self.df.groupby('year').agg({
            'salary_rub': 'mean',
            'name': 'count'
        }).round(2)

        php_stats = self.php_df.groupby('year').agg({
            'salary_rub': 'mean',
            'name': 'count'
        }).round(2)

        return (
            all_stats['salary_rub'],
            all_stats['name'],
            php_stats['salary_rub'],
            php_stats['name']
        )

    def process_geography_data(self):
        """Оптимизированная обработка географических данных"""
        def process_city_stats(df):
            total_vacancies = len(df)
            city_stats = df.groupby('area_name').agg({
                'salary_rub': 'mean',
                'name': 'count'
            }).round(2)
            city_stats['vacancy_share'] = (city_stats['name'] / total_vacancies * 100).round(2)
            return city_stats[city_stats['name'] >= total_vacancies * 0.01]

        return process_city_stats(self.df), process_city_stats(self.php_df)

    def process_skills(self):
        """Обработка навыков по годам"""
        def process_skills_by_year(df):
            skills_by_year = {}
            for year in df['year'].unique():
                year_df = df[df['year'] == year]
                year_skills = year_df[year_df['key_skills'].notna()]['key_skills'].str.split('\n').explode()
                if not year_skills.empty:
                    skills_by_year[year] = year_skills.value_counts().head(20)
            return skills_by_year

        # Обработка для всех вакансий
        all_skills_by_year = process_skills_by_year(self.df)

        # Обработка для PHP вакансий
        php_skills_by_year = process_skills_by_year(self.php_df)

        return all_skills_by_year, php_skills_by_year


    def create_graph(self, data, title, filename, graph_type='line'):
        """Универсальный метод создания графиков"""
        plt.figure(figsize=(12, 6))

        # Настраиваем базовый стиль
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.rcParams['font.size'] = 10

        if graph_type == 'line':
            plt.plot(data.index, data.values, marker='o', linewidth=2, color='#2c3e50')
            plt.grid(True)
            plt.xticks(rotation=45)
        elif graph_type == 'bar':
            colors = plt.cm.Set3(np.linspace(0, 1, len(data.head(20))))
            data.head(20).plot(kind='bar', color=colors)
            plt.xticks(rotation=45, ha='right')
        elif graph_type == 'pie':
            colors = plt.cm.Set3(np.linspace(0, 1, len(data.head(10))))
            plt.pie(
                data.head(10),
                labels=data.head(10).index,
                autopct='%1.1f%%',
                startangle=90,
                colors=colors
            )

        plt.title(title, pad=20, fontsize=12, fontweight='bold')
        plt.tight_layout()

        # Сохранение графика
        graph_path = os.path.join(settings.MEDIA_ROOT, 'graphs', filename)
        os.makedirs(os.path.dirname(graph_path), exist_ok=True)
        plt.savefig(graph_path, dpi=300, bbox_inches='tight')
        plt.close()

        return f'graphs/{filename}'

    def create_all_graphs(self):
        """Создание всех необходимых графиков"""
        graphs = []

        # Получаем все необходимые данные
        salary_data = self.process_salary_statistics()
        geo_data = self.process_geography_data()
        skills_data = self.process_skills()

        # Общая статистика
        graphs.append({
            'data': salary_data[0],
            'title': 'Динамика уровня зарплат по годам',
            'filename': 'general_salary_dynamics.png',
            'graph_type': 'salary',  # Изменено с 'type' на 'graph_type'
            'is_general': True
        })

        graphs.append({
            'data': salary_data[1],
            'title': 'Динамика количества вакансий по годам',
            'filename': 'general_count_dynamics.png',
            'graph_type': 'demand',  # Изменено с 'type' на 'graph_type'
            'is_general': True
        })

        graphs.append({
            'data': geo_data[0]['salary_rub'].sort_values(ascending=False),
            'title': 'Уровень зарплат по городам',
            'filename': 'general_city_salary.png',
            'graph_type': 'geography_salary',  # Изменено с 'type' на 'graph_type'
            'is_general': True
        })

        graphs.append({
            'data': geo_data[0]['vacancy_share'],
            'title': 'Доля вакансий по городам',
            'filename': 'general_city_share.png',
            'graph_type': 'geography_share',  # Изменено с 'type' на 'graph_type'
            'is_general': True
        })

        graphs.append({
            'data': skills_data[0],
            'title': 'ТОП-20 навыков',
            'filename': 'general_skills.png',
            'graph_type': 'skills',  # Изменено с 'type' на 'graph_type'
            'is_general': True
        })

        # PHP статистика
        graphs.append({
            'data': salary_data[2],
            'title': 'Динамика уровня зарплат PHP-программиста по годам',
            'filename': 'php_salary_dynamics.png',
            'graph_type': 'salary',  # Изменено с 'type' на 'graph_type'
            'is_general': False
        })

        graphs.append({
            'data': salary_data[3],
            'title': 'Динамика количества вакансий PHP-программиста по годам',
            'filename': 'php_count_dynamics.png',
            'graph_type': 'demand',  # Изменено с 'type' на 'graph_type'
            'is_general': False
        })

        graphs.append({
            'data': geo_data[1]['salary_rub'].sort_values(ascending=False),
            'title': 'Уровень зарплат PHP-программиста по городам',
            'filename': 'php_city_salary.png',
            'graph_type': 'geography_salary',  # Изменено с 'type' на 'graph_type'
            'is_general': False
        })

        graphs.append({
            'data': geo_data[1]['vacancy_share'],
            'title': 'Доля вакансий PHP-программиста по городам',
            'filename': 'php_city_share.png',
            'graph_type': 'geography_share',  # Изменено с 'type' на 'graph_type'
            'is_general': False
        })

        graphs.append({
            'data': skills_data[1],
            'title': 'ТОП-20 навыков PHP-программиста',
            'filename': 'php_skills.png',
            'graph_type': 'skills',  # Изменено с 'type' на 'graph_type'
            'is_general': False
        })

        # Создаем все графики
        result = []
        for graph in graphs:
            graph_type = 'pie' if 'share' in graph['graph_type'] else 'bar' if 'skills' in graph['graph_type'] or 'geography_salary' in graph['graph_type'] else 'line'
            file_path = self.create_graph(
                graph['data'],
                graph['title'],
                graph['filename'],
                graph_type
            )
            result.append({
                'title': graph['title'],
                'image': file_path,
                'graph_type': graph['graph_type'],
                'is_general': graph['is_general']
            })

        return result

