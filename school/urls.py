from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from .views import *


urlpatterns = [
    path('grades/', GradesOfSchoolView.as_view(), name='grades_of_school'),
    path('grade/<slug:grade_slug>/', SubjectsOfGradeView.as_view(), name='subjects_of_grade'),
    # path('grade/<slug:grade_slug>/subject/<slug:subject_slug>/', ChaptersOfCourseView.as_view(), name='chapters_of_course'),
    path('grade/<slug:grade_slug>/subject/<slug:subject_slug>/content/', ChaptersTopicsView.as_view(), name='chapters_topics'),
    # path('grade/<slug:grade_slug>/subject/<slug:subject_slug>/<slug:chapter_slug>/', TopicsOfChapterView.as_view(), name='topics_of_chapter'),
    path('grade/<slug:grade_slug>/subject/<slug:subject_slug>/<slug:chapter_slug>/<slug:topic_slug>/', VideosOfTopicView.as_view(), name='videos_of_topic'),
    path('random/', RandomTopicView.as_view(), name='random_topic'),
    path('empty_topics/', show_topics, name='empty_topics'),
    path('subjects_all/', SubjectsAllView.as_view(), name='subjects_all'),
    
]


"""
URL configuration for uacademy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""