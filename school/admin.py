from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .models import *


@admin.register(GradeType)
class GradeTypeAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'id', 'sort_order',)
    list_display_links = ('id', 'title')
    list_editable = ('is_active', 'sort_order',)
    ordering = ('sort_order',)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ( 'title', 'grade_type', 'is_active', 'slug', 'id', 'sort_order',)
    list_display_links = ('id', 'title',)
    list_editable = ('is_active', 'sort_order',)
    #fields = ('title', 'grade_type', 'is_active', 'sort_order',) #вказання порядку вивода редагованих полів
    #fieldsets =[('Основна інформація', {'fields': ('title', 'grade_type', 'is_active', 'sort_order',)})] #вказання порядку вивода редагованих полів з групуванням
    #readonly_fields = ('id', 'slug',)
    #prepopulated_fields={"slug":("title",)} #використовуючи цей функціонал не виходить приховати поле slug від користувача на формі додавання/редагування
    ordering = ('sort_order',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ( 'title', 'is_active', 'slug', 'id', 'sort_order',)
    list_display_links = ('id', 'title')
    list_editable = ('is_active', 'sort_order',)
    search_fields = ["id", "title",]
    ordering = ('sort_order',)


@admin.register(Science)
class ScienceAdmin(admin.ModelAdmin):
    list_display = ( 'title', 'is_active', 'slug', 'id', 'sort_order',)
    list_display_links = ('id', 'title')
    list_editable = ('is_active','sort_order',)
    search_fields = ["id", "title",]
    ordering = ('sort_order',)


@admin.register(GradeSubject)
class GradeSubjectAdmin(admin.ModelAdmin):
    list_display = ( 'title', 'is_active', 'id',)
    list_display_links = ('id', 'title')
    list_editable = ('is_active',)
    list_per_page = 20
    search_fields = ["id", "title"]
    readonly_fields = ('id',)
    ordering = ('grade', 'subject__sort_order')

    # def save_model(self, request, obj, form, change):
    #     try:
    #         obj.save()
    #     except IntegrityError as e:
    #         error_message = "Помилка IntegrityError: " + str(e)
    #         messages.error(request, error_message)


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ( 'course', 'sort_order', 'title', 'is_active', 'id',)
    list_display_links = ('id', 'title')
    list_editable = ('is_active', 'sort_order',)
    list_per_page = 20
    search_fields = ["id", "title", 'course__title']
    ordering = ('course', 'sort_order' ,)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ( 'get_course_title', 'get_chapter_title', 'sort_order', 'title', 'is_active', 'sort_order_full_dec','id',)
    list_display_links = ('id', 'title')
    list_editable = ('is_active', 'sort_order',)
    list_per_page = 20
    list_select_related = ['chapter',]
    search_fields = ["id", "title", 'chapter__title',]
    ordering = ('chapter', 'sort_order',)

    def get_course_title(self, obj):
        return obj.chapter.course.title
    
    def get_chapter_title(self, obj):
        return obj.chapter.title

    get_course_title.short_description = 'Клас-Предмет'
    get_chapter_title.short_description = 'Розділ'



@admin.register(TextBookAuthor)
class TextBookAuthorAdmin(admin.ModelAdmin):
    list_display = ( 'title', 'is_active', 'id',)
    list_display_links = ('id', 'title')
    list_editable = ('is_active',)
    list_per_page = 20
    search_fields = ["id", "title",]
    ordering = ('title',)


@admin.register(TextBook)
class TextBookAdmin(admin.ModelAdmin):
    list_display = ( 'title', 'course', 'description', 'is_active', 'id',)
    list_display_links = ('id', 'title')
    list_editable = ('is_active',)
    list_per_page = 20
    search_fields = ["id", "title",]
    ordering = ('title',)


@admin.register(VideoAuthor)
class VideoAuthorAdmin(admin.ModelAdmin):
    list_display = ( 'title', 'is_active', 'id',)
    list_display_links = ('id', 'title')
    list_editable = ('is_active',)
    list_per_page = 20
    search_fields = ["id", "title",]
    ordering = ('title',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ( 'title', 'is_active', 'slug', 'id', 'sort_order',)
    list_display_links = ('id', 'title')
    list_editable = ('is_active','sort_order',)
    list_per_page = 20
    search_fields = ["id", "title",]
    ordering = ('sort_order',)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'rating', 'link', 'is_active', 'get_tags', 'id', 'sort_order',)
    list_display_links = ('id', 'title')
    list_editable = ('is_active','sort_order',)
    list_per_page = 20
    search_fields = ['id', 'title', 'link', 'tags__title']
    ordering = ('science',)

    def get_tags(self, obj):
        tags = obj.tags.all()  # Отримуємо всі пов'язані об'єкти типу Tag
        return ", ".join(tag.title for tag in tags)
    
    get_tags.short_description = 'Теги'


@admin.register(TopicVideo)
class TopicVideoAdmin(admin.ModelAdmin):
    list_display = ('get_course_title', 'get_chapter_title', 'get_topic_title', 'video', 'title', 'is_active', 'id', 'sort_order')
    list_display_links = ('id', 'title')
    list_editable = ('is_active', 'sort_order')
    list_per_page = 20
    search_fields = ["id", "title",]
    readonly_fields = ('id',)
    ordering = ('title',)

    def get_course_title(self, obj):
        return obj.topic.chapter.course.title
    
    def get_chapter_title(self, obj):
        return obj.topic.chapter.title
    
    def get_topic_title(self, obj):
        return obj.topic.title

    get_course_title.short_description = 'Клас-Предмет'
    get_chapter_title.short_description = 'Розділ'
    get_topic_title.short_description = 'Тема'


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ( 'title', 'description', 'is_active', 'id', 'sort_order',)
    list_display_links = ('id', 'title')
    list_editable = ('is_active', 'sort_order',)
    ordering = ('sort_order',)


# admin.site.register(Grade, GradeAdmin)
# admin.site.register(GradeType, GradeTypeAdmin)
# admin.site.register(Subject, SubjectAdmin)
# admin.site.register(Science, ScienceAdmin)
# admin.site.register(GradeSubject, GradeSubjectAdmin)
# admin.site.register(Chapter, ChapterAdmin)


