from django.contrib import admin
from django.utils.html import format_html
from .models import MainPage, SalaryStatistics, GeographyData, Skill, Graph, LastVacancy

@admin.register(MainPage)
class MainPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_image')

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "Нет изображения"
    display_image.short_description = 'Изображение'

@admin.register(SalaryStatistics)
class SalaryStatisticsAdmin(admin.ModelAdmin):
    list_display = ('year', 'average_salary', 'vacancy_count', 'is_general')
    list_filter = ('year', 'is_general')
    search_fields = ('year',)
    ordering = ('-year',)

@admin.register(GeographyData)
class GeographyDataAdmin(admin.ModelAdmin):
    list_display = ('city', 'average_salary', 'vacancy_share', 'year', 'is_general')
    list_filter = ('year', 'is_general', 'city')
    search_fields = ('city',)
    ordering = ('-average_salary',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'count', 'year')
    list_filter = ('year',)
    search_fields = ('name',)
    ordering = ('-count',)

@admin.register(Graph)
class GraphAdmin(admin.ModelAdmin):
    list_display = ('title', 'graph_type', 'display_graph', 'is_general')
    list_filter = ('graph_type', 'is_general')
    search_fields = ('title',)

    def display_graph(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "Нет графика"
    display_graph.short_description = 'График'

@admin.register(LastVacancy)
class LastVacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'region', 'published_at')
    list_filter = ('published_at', 'region')
    search_fields = ('title', 'company')
    ordering = ('-published_at',)

admin.site.site_header = "Администрирование PHP Аналитики"
admin.site.site_title = "PHP Аналитика"
admin.site.index_title = "Управление данными"
