from datetime import datetime
from django.views.generic import TemplateView, DetailView, ListView, FormView, View
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.db.models import Count
from django.db.models import Prefetch
from itertools import groupby
import math
from .models import *
from .forms import *

class GradesOfSchoolView(ListView):
    model = Grade
    template_name = 'school/grades_of_school.html'
    context_object_name = 'grades'

    def get_queryset(self):
        return Grade.objects.filter(is_active=True).order_by('sort_order')
    

class SubjectsOfGradeView(View):
    template_name = 'school/subjects_of_grade.html'
    
    def get(self, request, grade_slug):
        # Знайти об'єкт Grade або відобразити 404 помилку, якщо такий не існує
        grade = get_object_or_404(Grade, slug=grade_slug)
        courses = GradeSubject.objects.filter(grade=grade)
        subjects = Subject.objects.filter(gradesubject__in=courses, is_active=True).distinct().order_by('sort_order')

        topic_chapter_list = []
        for subject in subjects:
            subject_slug=subject.slug
            chapters_topics_view = ChaptersTopicsView()  # Створюємо екземпляр класу ChaptersTopicsView
            response = chapters_topics_view.get(request, grade_slug, subject_slug)  # Викликаємо метод класу ChaptersTopicsView
            topic_current = chapters_topics_view.topic_current
            chapter_current = Chapter.objects.filter(topic=topic_current).distinct().first()
            #print(f'!!!Поточна тема: {topic_current}')
            # print(f'!!!Поточний розділ: {chapter_current}')
            topic_chapter_list.append((subject, chapter_current, topic_current))
        
        # print(f'!!!Список поточних розділів і тем: {topic_chapter_list}')

        for subject, topic, chapter in topic_chapter_list:
            if hasattr(chapter, 'slug'):
                chapter_slug = chapter.slug
                # print(f'!!!Список слагів поточних розділів: {chapter_slug}')

        context = {'grade': grade,
                   'subjects': subjects,
                   'topic_current': topic_current,
                   'chapter_current': chapter_current,
                   'topic_chapter_list': topic_chapter_list,
                   }
        return render(request, self.template_name, context)


# def subject_list(request, slug):
#     # Знайти об'єкт Grade або відобразити 404 помилку, якщо такий не існує
#     grade = get_object_or_404(Grade, slug=slug)
    
#     # Знайти всі курси (GradeSubject) з вибраним Grade
#     courses = GradeSubject.objects.filter(grade=grade)
    
#     # Отримати унікальні Subject, пов'язані з цими курсами
#     subjects = Subject.objects.filter(course__in=courses).distinct()
    
#     return render(request, 'school/select_subject.html', {'grade': grade, 'subjects': subjects})


class ChaptersOfCourseView(View):
    template_name = 'school/chapters_of_course.html'
    
    def get(self, request, grade_slug, subject_slug):
        # Знайти об'єкт або відобразити 404 помилку, якщо такий не існує
        grade = get_object_or_404(Grade, slug=grade_slug)
        subject = get_object_or_404(Subject, slug=subject_slug)
        
        course = GradeSubject.objects.filter(grade=grade, subject=subject)
        
        chapters = Chapter.objects.filter(course__in=course, is_active=True).distinct().order_by('sort_order')
        
        context = {'grade': grade,
                   'subject': subject,
                   'chapters': chapters}
        return render(request, self.template_name, context)


class ChaptersTopicsView(View):
    template_name = 'school/chapters_topics.html'
    
    def get(self, request, grade_slug, subject_slug):
        # Знайти об'єкт або відобразити 404 помилку, якщо такий не існує
        grade = get_object_or_404(Grade, slug=grade_slug)
        subject = get_object_or_404(Subject, slug=subject_slug)
        course = GradeSubject.objects.filter(grade=grade, subject=subject).distinct().first()  # вибраний курс

        chapters = Chapter.objects.filter(course=course, is_active=True).order_by('sort_order')
        topics = Topic.objects.filter(chapter__in=chapters, is_active=True).order_by('sort_order_full')
        # print(f'Список тем: {topics}')

        # chapters = chapters.prefetch_related(
        #     Prefetch('topic_set', queryset=Topic.objects.filter(is_active=True).order_by('sort_order_full')))
        
        chapters = chapters.prefetch_related(
            Prefetch('topic_set', queryset=topics.filter(is_active=True).order_by('sort_order_full').annotate(video_exist=Count('topicvideo'))
        ))
        
        days_for_today, days_per_year = calculate_school_days()  
        
        topic_current = None
        topics_num = topics.count()
        if topics_num > 0:
            print(f'Кількість тем: {topics_num}')
            days_per_topic = round(days_per_year/topics_num)
            print(f'Днів на тему: {days_per_topic}')
            number_of_topic_test = days_for_today/days_per_topic
            number_of_topic = math.ceil(days_for_today/days_per_topic)
            print(f'Номер поточної теми: {number_of_topic_test}')
            print(f'Номер поточної теми після округлення: {number_of_topic}')
            if number_of_topic < 1: number_of_topic = 1
            if number_of_topic == topics_num: number_of_topic = topics_num
            topic_current = topics[number_of_topic-1]
            print(f'Поточна тема: {topic_current}')

        self.topic_current = topic_current
        
        context = {'grade': grade,
                   'subject': subject,
                   'course': course, 
                   'chapters': chapters, 
                   'topics': topics,
                   'topic_current': topic_current,
                   }
        
        return render(request, self.template_name, context)



class VideosOfTopicView(View):
    template_name = 'school/videos_of_topic.html'
    
    def get(self, request, grade_slug, subject_slug, chapter_slug, topic_slug):
        # Знайти об'єкт або відобразити 404 помилку, якщо такий не існує
        grade = get_object_or_404(Grade, slug=grade_slug)
        subject = get_object_or_404(Subject, slug=subject_slug)
        course = GradeSubject.objects.filter(grade=grade, subject=subject).distinct().first()
        chapter = get_object_or_404(Chapter, slug=chapter_slug)
        topic = get_object_or_404(Topic, slug=topic_slug)

        # Шукаємо всі відео вибраної теми і сортуємо їх
        topic_video = TopicVideo.objects.filter(topic=topic, is_active=True).order_by('sort_order').prefetch_related('video')
        videos = []
        for item in topic_video:
            video = item.video
            topic_video_desc = item.description  # Поле description з topic_video
            video.topic_video_desc = topic_video_desc  # Додавання поля topic_video_desc до video
            videos.append(video)
        videos = sorted(videos, key=lambda item: (item.sort_order, -item.rating))

        chapter_pre, chapter_next, topic_pre, topic_next = self.find_previous_next_topics(course, topic)
        nav_pre = bool(topic_pre)
        nav_next = bool(topic_next)
        
        context = {'grade': grade,
                   'subject': subject,
                   'chapter': chapter,
                   'chapter_pre': chapter_pre,
                   'chapter_next': chapter_next,
                   'topic': topic,
                   'topic_pre':topic_pre,
                   'topic_next': topic_next,
                   'nav_pre': nav_pre,
                   'nav_next': nav_next,
                   'videos': videos}
        return render(request, self.template_name, context)
    

    def find_previous_next_topics(self, course, topic):
        chapters_of_course = Chapter.objects.filter(course=course, is_active=True).distinct()  #всі розділи курсу
        topics_of_chapters = Topic.objects.filter(chapter__in=chapters_of_course, is_active=True).distinct().order_by("sort_order_full")  #всі теми курсу
        # print(f'всі теми курсу: {topics_of_chapters}')

        # print(f'поточна тема: {topic}')
        topic_pre = topics_of_chapters.filter(sort_order_full__lt=topic.sort_order_full).order_by("sort_order_full").last()  #попередня тема
        chapter_pre = Chapter.objects.filter(topic=topic_pre).distinct().first()
        # print(f'попередня тема: {topic_pre}')

        topic_next = topics_of_chapters.filter(sort_order_full__gt=topic.sort_order_full).order_by("sort_order_full").first() #наступна тема
        chapter_next = Chapter.objects.filter(topic=topic_next).distinct().first()
        # print(f'наступна тема: {topic_next}')

        return chapter_pre, chapter_next, topic_pre, topic_next



class RandomTopicView(View):
    template_name = 'school/videos_of_topic.html'

    def get(self, request):
        topics_with_video = TopicVideo.objects.filter(is_active=True).values_list('topic', flat=True).distinct()
        if topics_with_video:
            random_topic_id = random.choice(topics_with_video)
            random_topic = Topic.objects.get(id=random_topic_id)
            topic = random_topic
        else:
            topic = random_topic  # придумати щось для цього випадку

        chapter = Chapter.objects.filter(topic=topic).distinct().first()
        course = GradeSubject.objects.filter(chapter=chapter).distinct().first()
        subject = Subject.objects.filter(gradesubject=course).distinct().first()
        grade = Grade.objects.filter(gradesubject=course).distinct().first()

        # Шукаємо всі відео вибраної теми і сортуємо їх
        topic_video = TopicVideo.objects.filter(topic=topic, is_active=True).order_by('sort_order').prefetch_related('video')
        videos = []
        for item in topic_video:
            video = item.video
            topic_video_desc = item.description  # Поле description з topic_video
            video.topic_video_desc = topic_video_desc  # Додавання поля topic_video_desc до video
            videos.append(video)
        videos = sorted(videos, key=lambda item: (item.sort_order, -item.rating))

        pre_next_topic = VideosOfTopicView()
        chapter_pre, chapter_next, topic_pre, topic_next = pre_next_topic.find_previous_next_topics(course, topic)
        nav_pre = bool(topic_pre)
        nav_next = bool(topic_next)

        context = {'grade': grade,
                   'subject': subject,
                   'chapter': chapter,
                   'chapter_pre': chapter_pre,
                   'chapter_next': chapter_next,
                   'topic_video': topic_video,
                   'topic': topic,
                   'topic_pre':topic_pre,
                   'topic_next': topic_next,
                   'nav_pre': nav_pre,
                   'nav_next': nav_next,
                   'videos': videos
                   }
        return render(request, self.template_name, context)


class SubjectsAllView(ListView):
    model = Subject
    template_name = 'school/subjects_all.html'
    context_object_name = 'subjects'


def show_topics(request):
    return render(request, 'school/empty_topics.html')


def calculate_school_days():
    current_date = datetime.now()
    #current_date = datetime(2023, 11, 15)  # Рік, місяць, день для тестування

    current_year = current_date.year
    date_start1 = datetime(current_year - 1, 9, 2)  # Рік, місяць, день - для дат до 01.09
    date_finish1 = datetime(current_year, 5, 30)  # Рік, місяць, день - для дат до 01.09
    date_start2 = datetime(current_year, 9, 1)  # Рік, місяць, день - для дат після 01.09
    date_finish2 = datetime(current_year + 1, 5, 15)  # Рік, місяць, день - для дат після 01.09

    if date_finish1 <= current_date < date_start2:
        current_date = date_finish1

    if current_date <= date_finish1:
        date_start = date_start1
        date_finish = date_finish1
    else:
        date_start = date_start2
        date_finish = date_finish2

    days_per_year = date_finish - date_start
    # print(f'днів за навчальний рік: {days_per_year}')
    days_for_today = current_date - date_start
    # print(f'днів навчання до сьогодні: {days_for_today}')
    number_of_days_per_year = days_per_year.days
    # print(f'днів в навчальному році: {number_of_days_per_year}')
    number_of_days_for_today = days_for_today.days
    # print(f'днів навчання до сьогодні: {number_of_days_for_today}')

    return number_of_days_for_today, number_of_days_per_year
