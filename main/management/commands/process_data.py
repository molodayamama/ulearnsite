from django.core.management.base import BaseCommand
from main.utils import DataProcessor
from main.models import SalaryStatistics, GeographyData, Skill, Graph
import os

class Command(BaseCommand):
    help = 'Process vacancy data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_path = options['csv_file']

        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'File not found: {csv_path}'))
            return

        try:
            self.stdout.write(self.style.SUCCESS(f'Starting data processing from {csv_path}'))

            # Очищаем старые данные
            SalaryStatistics.objects.all().delete()
            GeographyData.objects.all().delete()
            Skill.objects.all().delete()
            Graph.objects.all().delete()

            # Создаем экземпляр обработчика данных
            processor = DataProcessor(csv_path)

            # Обработка статистики зарплат (общая и PHP)
            self.stdout.write('Processing salary statistics...')
            all_salary_by_year, all_count_by_year, php_salary_by_year, php_count_by_year = processor.process_salary_statistics()

            # Сохранение общей статистики
            for year in all_salary_by_year.index:
                SalaryStatistics.objects.create(
                    year=year,
                    average_salary=all_salary_by_year[year],
                    vacancy_count=all_count_by_year[year],
                    is_general=True
                )
                self.stdout.write(f'Saved general statistics for year {year}')

            # Сохранение PHP статистики
            for year in php_salary_by_year.index:
                SalaryStatistics.objects.create(
                    year=year,
                    average_salary=php_salary_by_year[year],
                    vacancy_count=php_count_by_year[year],
                    is_general=False
                )
                self.stdout.write(f'Saved PHP statistics for year {year}')

            # Обработка географии (общая и PHP)
            self.stdout.write('Processing geography data...')
            all_city_stats, php_city_stats = processor.process_geography_data()

            # Сохранение общей географии
            for city, data in all_city_stats.iterrows():
                GeographyData.objects.create(
                    city=city,
                    average_salary=data['salary_rub'],
                    vacancy_share=data['vacancy_share'],
                    year=2024,
                    is_general=True
                )
                self.stdout.write(f'Saved general geography data for {city}')

            # Сохранение PHP географии
            for city, data in php_city_stats.iterrows():
                GeographyData.objects.create(
                    city=city,
                    average_salary=data['salary_rub'],
                    vacancy_share=data['vacancy_share'],
                    year=2024,
                    is_general=False
                )
                self.stdout.write(f'Saved PHP geography data for {city}')

            # Обработка навыков (общая и PHP)
            self.stdout.write('Processing skills...')
            all_skills, php_skills = processor.process_skills()

            # Сохранение общих навыков
            for skill, count in all_skills.head(20).items():
                Skill.objects.create(
                    name=skill,
                    year=2024,
                    count=count,
                    is_general=True
                )
                self.stdout.write(f'Saved general skill {skill}')

            # Сохранение PHP навыков
            for skill, count in php_skills.head(20).items():
                Skill.objects.create(
                    name=skill,
                    year=2024,
                    count=count,
                    is_general=False
                )
                self.stdout.write(f'Saved PHP skill {skill}')

            # Создание графиков
            self.stdout.write('Creating graphs...')

            # Графики общей статистики
            salary_graph_path = processor.create_salary_graph(
                all_salary_by_year,
                'Динамика уровня зарплат по годам',
                'general_salary_dynamics.png',
                is_general=True
            )
            Graph.objects.create(
                title='Динамика уровня зарплат по годам',
                image=salary_graph_path,
                graph_type='salary',
                is_general=True
            )

            count_graph_path = processor.create_count_graph(
                all_count_by_year,
                'Динамика количества вакансий по годам',
                'general_count_dynamics.png',
                is_general=True
            )
            Graph.objects.create(
                title='Динамика количества вакансий по годам',
                image=count_graph_path,
                graph_type='demand',
                is_general=True
            )

            geography_graph_path = processor.create_geography_graph(
                all_city_stats,
                'Распределение вакансий по городам',
                'general_geography.png',
                is_general=True
            )
            Graph.objects.create(
                title='Распределение вакансий по городам',
                image=geography_graph_path,
                graph_type='geography',
                is_general=True
            )

            skills_graph_path = processor.create_skills_graph(
                all_skills,
                'ТОП-20 навыков',
                'general_skills.png',
                is_general=True
            )
            Graph.objects.create(
                title='ТОП-20 навыков',
                image=skills_graph_path,
                graph_type='skills',
                is_general=True
            )

            # Графики PHP статистики
            php_salary_graph_path = processor.create_salary_graph(
                php_salary_by_year,
                'Динамика уровня зарплат PHP-программиста по годам',
                'php_salary_dynamics.png',
                is_general=False
            )
            Graph.objects.create(
                title='Динамика уровня зарплат PHP-программиста по годам',
                image=php_salary_graph_path,
                graph_type='salary',
                is_general=False
            )

            php_count_graph_path = processor.create_count_graph(
                php_count_by_year,
                'Динамика количества вакансий PHP-программиста по годам',
                'php_count_dynamics.png',
                is_general=False
            )
            Graph.objects.create(
                title='Динамика количества вакансий PHP-программиста по годам',
                image=php_count_graph_path,
                graph_type='demand',
                is_general=False
            )

            php_geography_graph_path = processor.create_geography_graph(
                php_city_stats,
                'Распределение вакансий PHP-программиста по городам',
                'php_geography.png',
                is_general=False
            )
            Graph.objects.create(
                title='Распределение вакансий PHP-программиста по городам',
                image=php_geography_graph_path,
                graph_type='geography',
                is_general=False
            )

            php_skills_graph_path = processor.create_skills_graph(
                php_skills,
                'ТОП-20 навыков PHP-программиста',
                'php_skills.png',
                is_general=False
            )
            Graph.objects.create(
                title='ТОП-20 навыков PHP-программиста',
                image=php_skills_graph_path,
                graph_type='skills',
                is_general=False
            )

            self.stdout.write(self.style.SUCCESS('Successfully processed vacancy data'))

            # Выводим итоговую статистику
            self.stdout.write(f'Total statistics records: {SalaryStatistics.objects.count()}')
            self.stdout.write(f'Total geography records: {GeographyData.objects.count()}')
            self.stdout.write(f'Total skills records: {Skill.objects.count()}')
            self.stdout.write(f'Total graphs: {Graph.objects.count()}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing: {str(e)}'))
