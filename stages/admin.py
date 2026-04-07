from django.contrib import admin
from .models import Category, Stage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'category', 'contact_email', 'deadline')
    list_filter = ('category',)
    search_fields = ('title', 'company', 'skills', 'contact_email')