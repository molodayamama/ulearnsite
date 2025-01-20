from django.db import models

class MainPage(models.Model):
    """Модель для главной страницы"""
    title = models.CharField('Заголовок', max_length=200, default='PHP-программист')
    description = models.TextField('Описание профессии')
    image = models.ImageField('Изображение', upload_to='profession_images/')

    class Meta:
        verbose_name = 'Главная страница'
        verbose_name_plural = 'Главная страница'

    def __str__(self):
        return self.title

class Skill(models.Model):
    """Модель для навыков"""
    name = models.CharField('Название навыка', max_length=100)
    year = models.IntegerField('Год')
    count = models.IntegerField('Количество упоминаний')
    is_general = models.BooleanField('Общая статистика', default=True)  # Добавляем это поле

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'
        ordering = ['-count']

    def __str__(self):
        return f"{self.name} ({self.year})"

class SalaryStatistics(models.Model):
    """Модель для статистики зарплат"""
    year = models.IntegerField('Год')
    average_salary = models.DecimalField('Средняя зарплата', max_digits=10, decimal_places=2)
    vacancy_count = models.IntegerField('Количество вакансий')
    is_general = models.BooleanField('Общая статистика', default=True)

    class Meta:
        verbose_name = 'Статистика зарплат'
        verbose_name_plural = 'Статистика зарплат'
        ordering = ['year']

    def __str__(self):
        return f"Статистика за {self.year} год"

class GeographyData(models.Model):
    """Модель для географических данных"""
    city = models.CharField('Город', max_length=100)
    average_salary = models.DecimalField('Средняя зарплата', max_digits=10, decimal_places=2)
    vacancy_share = models.DecimalField('Доля вакансий', max_digits=5, decimal_places=2)
    year = models.IntegerField('Год')
    is_general = models.BooleanField('Общая статистика', default=True)

    class Meta:
        verbose_name = 'География'
        verbose_name_plural = 'География'
        ordering = ['-average_salary']

    def __str__(self):
        return f"{self.city} ({self.year})"

class Graph(models.Model):
    """Модель для хранения графиков"""
    GRAPH_TYPES = [
        ('salary', 'График зарплат'),
        ('counts', 'График количества вакансий'),
        ('skills', 'График навыков'),
        ('geography', 'График географии'),
    ]

    title = models.CharField('Заголовок', max_length=200)
    image = models.ImageField('График', upload_to='graphs/')
    graph_type = models.CharField('Тип графика', max_length=20, choices=GRAPH_TYPES)
    year = models.IntegerField('Год', null=True, blank=True)
    is_general = models.BooleanField('Общая статистика', default=True)

    class Meta:
        verbose_name = 'График'
        verbose_name_plural = 'Графики'
        ordering = ['graph_type', 'year']

    def __str__(self):
        return self.title

