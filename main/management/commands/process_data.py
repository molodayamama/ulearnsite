from django.core.management.base import BaseCommand
from main.utils import DataProcessor
from main.models import SalaryStatistics, GeographyData, Skill, Graph
import os


class Command(BaseCommand):
    help = "Process vacancy data from CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    def handle(self, *args, **options):
        csv_path = options["csv_file"]
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"File not found: {csv_path}"))
            return

        try:
            self.stdout.write(
                self.style.SUCCESS(f"Starting data processing from {csv_path}")
            )

            # Очищаем старые данные
            SalaryStatistics.objects.all().delete()
            GeographyData.objects.all().delete()
            Skill.objects.all().delete()
            Graph.objects.all().delete()

            # Создаем экземпляр обработчика данных
            processor = DataProcessor(csv_path)

            # Обработка и сохранение всех данных
            self.stdout.write("Processing data...")

            # Статистика зарплат
            all_salary, all_count, php_salary, php_count = (
                processor.process_salary_statistics()
            )

            # Сохранение статистики
            for year in all_salary.index:
                SalaryStatistics.objects.create(
                    year=year,
                    average_salary=all_salary[year],
                    vacancy_count=all_count[year],
                    is_general=True,
                )
                if year in php_salary.index:
                    SalaryStatistics.objects.create(
                        year=year,
                        average_salary=php_salary[year],
                        vacancy_count=php_count[year],
                        is_general=False,
                    )

            # География
            all_geo, php_geo = processor.process_geography_data()

            # Сохранение географии
            for city in all_geo.index:
                GeographyData.objects.create(
                    city=city,
                    average_salary=all_geo.loc[city, "salary_rub"],
                    vacancy_share=all_geo.loc[city, "vacancy_share"],
                    year=2024,
                    is_general=True,
                )

            for city in php_geo.index:
                GeographyData.objects.create(
                    city=city,
                    average_salary=php_geo.loc[city, "salary_rub"],
                    vacancy_share=php_geo.loc[city, "vacancy_share"],
                    year=2024,
                    is_general=False,
                )

            # Навыки
            all_skills, php_skills = processor.process_skills()

            # Сохранение навыков
            for skill, count in all_skills.head(20).items():
                Skill.objects.create(
                    name=skill, year=2024, count=count, is_general=True
                )

            for skill, count in php_skills.head(20).items():
                Skill.objects.create(
                    name=skill, year=2024, count=count, is_general=False
                )

            # Создание всех графиков
            self.stdout.write("Creating graphs...")
            graphs = processor.create_all_graphs()

            # Сохранение графиков ()
            for graph_data in graphs:
                Graph.objects.create(
                    title=graph_data["title"],
                    image=graph_data["image"],
                    graph_type=graph_data[
                        "graph_type"
                    ],
                    is_general=graph_data["is_general"],
                )

            self.stdout.write(self.style.SUCCESS("Successfully processed vacancy data"))

            # Итоговая статистика
            self.stdout.write(
                f"Total statistics records: {SalaryStatistics.objects.count()}"
            )
            self.stdout.write(
                f"Total geography records: {GeographyData.objects.count()}"
            )
            self.stdout.write(f"Total skills records: {Skill.objects.count()}")
            self.stdout.write(f"Total graphs: {Graph.objects.count()}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing: {str(e)}"))
            raise
