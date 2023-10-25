from django.db import IntegrityError
from django.db import transaction
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from autoslug import AutoSlugField
from slugify import slugify
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.core.validators import MinValueValidator, MaxValueValidator
import random
import re


# ---- Тип школи -------------------
class GradeType(models.Model):
    title = models.CharField(
        verbose_name='Тип школи',
        max_length=50, 
        unique=True, 
        )
    is_active = models.BooleanField(
        verbose_name='Виводити', 
        default=True
        )
    sort_order = models.IntegerField(
        verbose_name="Порядок виводу",
        help_text="Якщо поле залишиться пустим, то після збереженні елемент буде виводитися останнім.",
        null=True,
        blank=True,
        )
    objects = models.Manager()  # для можливості створення запитів до БД

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Тип школи'
        verbose_name_plural = 'Додатковий довідник: Типи школи'

    
# ---- Клас -------------------
class Grade(models.Model):
    title = models.CharField(
        verbose_name='Назва класу', 
        help_text='Додайте до назви слово клас, щоб користувачу було більш зрозуміло.',
        max_length=50, 
        unique=True, 
        )
    grade_type = models.ForeignKey(
        GradeType, 
        verbose_name="Тип школи",
        on_delete=models.PROTECT, 
        )
    is_active = models.BooleanField(
        verbose_name='Виводити',
        default=True,
        )
    sort_order = models.IntegerField(
        verbose_name="Порядок виводу", 
        help_text="Якщо поле залишиться пустим, то після збереженні елемент буде виводитися останнім.",
        null=True,
        blank=True,
        )
    slug = models.SlugField(
        verbose_name="slug",
        help_text="заповнюється автоматично",
        unique=True,
        blank=False,
        editable=False,
        max_length=50,
        )
    objects = models.Manager()  # для можливості створення запитів до БД

    def __str__(self):
        return self.title
    
    def save(self):
        self.slug = slugify(self.title)
        super(Grade, self).save()

    def get_absolute_url(self):
       # return reverse ('subjects', kwargs={'slug':self.slug})
       # return f"/courses/n/"
         return f"/courses/{self.slug}/"

    class Meta:
        verbose_name = 'Клас'
        verbose_name_plural = 'Довідник 1: Класи'


# ---- Наукова дисципліна -------------------
class Science(models.Model):
    title = models.CharField(
        verbose_name="Назва наукової дисципліни",
        max_length=100, 
        unique=True,
        )
    is_active = models.BooleanField(
        verbose_name="Виводити",
        default=True,
        )
    sort_order = models.IntegerField(
        verbose_name="Порядок виводу",
        help_text="Якщо поле залишиться пустим, то після збереженні елемент буде виводитися останнім.",
        null=True,
        blank=True,
        )
    slug = models.SlugField(
        verbose_name="slug",
        help_text="заповнюється автоматично",
        unique=True,
        blank=False,
        editable=False,
        max_length=100,
        )
    objects = models.Manager()  # для можливості створення запитів до БД

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Наукова дисципліна'
        verbose_name_plural = 'Додатковий довідник: Наукові дисципліни'


# ---- Предмет -------------------
class Subject(models.Model):
    title = models.CharField(
        verbose_name="Назва предмету",
        max_length=100, 
        unique=True,
        )
    is_active = models.BooleanField(
        verbose_name="Виводити",
        default=True,
        )
    sort_order = models.IntegerField(
        verbose_name="Порядок виводу",
        help_text="Якщо поле залишиться пустим, то після збереженні елемент буде виводитися останнім.",
        null=True,
        blank=True,
        )
    slug = models.SlugField(
        verbose_name="slug",
        help_text="заповнюється автоматично",
        unique=True,
        blank=False,
        editable=False,
        max_length=100,
        )
    objects = models.Manager()  # для можливості створення запитів до БД

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Довідник 2: Предмети'


# ---- Курс (Клас-Предмет) -------------------
class GradeSubject(models.Model):
    grade = models.ForeignKey(
        Grade,
        verbose_name="Клас",
        on_delete=models.PROTECT,
        )
    subject = models.ForeignKey(
        Subject,
        verbose_name="Предмет",
        on_delete=models.PROTECT,
        )
    title = models.CharField(
        verbose_name="Клас-Предмет (курс)",
        help_text="заповнюється автоматично",
        max_length=150,
        blank=True,
        unique=True,
        editable=False,
        )
    is_active = models.BooleanField(
        verbose_name="Активно", 
        default=True,
        )
    objects = models.Manager()  # для можливості створення запитів до БД

    def __str__(self):
        return self.grade.title+' - '+self.subject.title

    def save(self):
        if not self.title:
            self.title = f"{self.grade.title} - {self.subject.title}"
        super(GradeSubject, self).save()

    class Meta:
        verbose_name = 'Курс (Клас-Предмет)'
        verbose_name_plural = 'Довідник 3: Курси (Клас-Предмет)'
        unique_together = ('grade', 'subject')


# ---- Розділ -------------------
class Chapter(models.Model):
    course = models.ForeignKey(
        GradeSubject,
        verbose_name="Курс (Клас-Предмет)",
        on_delete=models.PROTECT,
        )
    sort_order = models.IntegerField(
        verbose_name="Номер розділу", 
        help_text="Номер розділу потрібен, щоб вивести розділи в правильному порядку",
        null=False,
        blank=False,
        )
    title = models.CharField(
        verbose_name="Назва розділу",
        max_length=255,
        unique=True,
        )
    description = models.TextField(
        verbose_name="Опис розділу",
        max_length=2000, 
        blank=True,
        )
    is_active = models.BooleanField(
        verbose_name="Виводити",
        default=True,
        )
    slug = models.SlugField(
        verbose_name="slug",
        help_text="заповнюється автоматично",
        unique=True,
        blank=False,
        editable=False,
        max_length=255,
        )
    objects = models.Manager()  # для можливості створення запитів до БД

    def save(self, *args, **kwargs):
        # Генеруємо Slug на основі поля title
        self.slug = slugify(self.title)
        super(Chapter, self).save(*args, **kwargs)

    def __str__(self):
        return self.course.title + ' - ' + self.title

    class Meta:
        verbose_name = 'Розділ'
        verbose_name_plural = '1. Розділи'



# ---- Тема -------------------
class Topic(models.Model):
    chapter= models.ForeignKey(
        Chapter,
        verbose_name="Розділ",
        on_delete=models.PROTECT,
        )
    sort_order = models.IntegerField(
        verbose_name="Номер теми", 
        help_text="Номер теми потрібен, щоб вивести теми в правильному порядку",
        null=False,
        blank=False,
        )
    title = models.CharField(
        verbose_name="Назва теми",
        max_length=255,
        unique=True,
        )
    description = models.TextField(
        verbose_name="Опис теми",
        max_length=2000, 
        blank=True,
        )
    science = models.ForeignKey(
        Science,
        verbose_name="Наукова дисципліна",
        on_delete=models.PROTECT,
        )
    is_active = models.BooleanField(
        verbose_name="Виводити",
        default=True,
        )
    sort_order_full_dec = models.DecimalField(
        verbose_name = "Порядок виводу",
        help_text="Розраховується автоматично",
        max_digits=8, # Максимальна кількість цифр, включаючи десяткові
        decimal_places = 4, # Кількість цифр після десяткової коми
        null=True,
        blank=True,
        editable=False,
    )
    slug = models.SlugField(
        verbose_name="slug",
        help_text="заповнюється автоматично",
        unique=True,
        blank=False,
        editable=False,
        max_length=255,
        )
    objects = models.Manager()  # для можливості створення запитів до БД

    def __str__(self):
        return self.chapter.course.title + '-' + self.chapter.title + '-' + self.title
    
    def save(self):
        self.sort_order_full_dec = self.chapter.sort_order * 1 + self.sort_order * 0.0001
        super(Topic, self).save()

    class Meta:
        verbose_name = 'Тема'
        verbose_name_plural = '2. Теми'


# ---- Автори підручників -------------------
class TextBookAuthor(models.Model):
    title = models.CharField(
        verbose_name="Автор(и) підручника",
        help_text="Вкажіть ПІБ у вигляді ''Т.Тарасенко''",
        max_length=255,
        unique=True,
        )
    is_active = models.BooleanField(
        verbose_name="Виводити",
        default=True,
        )
    slug = models.SlugField(
        verbose_name="slug",
        help_text="заповнюється автоматично",
        unique=True,
        blank=False,
        editable=False,
        max_length=255,
        )
    objects = models.Manager()  # для можливості створення запитів до БД

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Автор підручника'
        verbose_name_plural = 'Довідник для підручників: Автори підручників'


# ---- Підручники -------------------
class TextBook(models.Model):
    course = models.ForeignKey(
        GradeSubject,
        verbose_name="Курс (Клас-Предмет)",
        on_delete=models.PROTECT,
        )
    book_author = models.ForeignKey(
        TextBookAuthor,
        verbose_name="Автори підручника",
        on_delete=models.PROTECT,
        )
    title = models.CharField(
        verbose_name="Назва підручника",
        max_length=255,
        unique=True,
        )
    description = models.TextField(
        verbose_name="Опис книги",
        max_length=2000, 
        blank=True,
        )
    is_active = models.BooleanField(
        verbose_name="Виводити",
        default=True,
        )
    slug = models.SlugField(
        verbose_name="slug",
        help_text="заповнюється автоматично",
        unique=True,
        blank=False,
        editable=False,
        max_length=255,
        )
    objects = models.Manager()  # для можливості створення запитів до БД

    def __str__(self):
        return self.title + ' ' + self.book_author.title

    class Meta:
        verbose_name = 'Підручник'
        verbose_name_plural = 'Довідник для підручників: Підручники'


# ---- Автори відео, канали -------------------
class  VideoAuthor(models.Model):
    title = models.CharField(
        verbose_name="Назва каналу, автора",
        max_length=255,
        unique=True,
        )
    is_active = models.BooleanField(
        verbose_name="Виводити",
        default=True,
        )
    slug = models.SlugField(
        verbose_name="slug",
        help_text="заповнюється автоматично",
        unique=True,
        blank=False,
        editable=False,
        max_length=255,
        )
    objects = models.Manager()  # для можливості створення запитів до БД

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Назва каналу, автора'
        verbose_name_plural = 'Довідник для відео: Канали, автори відео'



# ---- Рівень знань учня -------------------
class Level(models.Model):
    title = models.CharField(
        verbose_name="Назва рівня",
        max_length=50,
        )
    description = models.TextField(
        verbose_name="Опис рівня",
        max_length=200, 
        blank=True,
        )
    sort_order = models.IntegerField(
        verbose_name="Порядок виводу", 
        help_text="Якщо поле залишиться пустим, то після збереженні елемент буде виводитися останнім.",
        null=True,
        blank=True,
        )
    is_active = models.BooleanField(
        verbose_name="Виводити",
        default=True,
        )
    objects = models.Manager()  # для можливості створення запитів до БД

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Рівень знань учня'
        verbose_name_plural = 'Додатковий довідник: Рівні знань учнів'


# ---- Теги для відео -------------------
class Tag(models.Model):
    title = models.CharField(
        verbose_name="Назва тегу (українською)",
        max_length=100, 
        unique=True,
        )
    sort_order = models.IntegerField(
        verbose_name="Порядок виводу", 
        help_text="Якщо поле залишиться пустим, то після збереженні елемент буде виводитися останнім.",
        null=True,
        blank=True,
        )
    is_active = models.BooleanField(
        verbose_name="Виводити",
        default=True,
        )
    slug = models.SlugField(
        verbose_name="slug",
        help_text="заповнюється автоматично",
        unique=True,
        blank=False,
        editable=False,
        max_length=255,
        )
    objects = models.Manager()  # для можливості створення запитів до БД

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Тег для відео'
        verbose_name_plural = 'Довідник для відео: Теги для відео'



# Власний валідатор для перевірки, чи URL починається з "https://"
def validate_https_url(value):
    if not value.startswith("https://www.youtube.com/embed/"):
        raise ValidationError("URL має починатися з 'https://www.youtube.com/embed/'.")


def validate_html_code(value):
    iframe_regex = r'<iframe [^>]*src="https://www\.youtube\.com/embed/[^"]+"[^>]*>'

    if not re.match(iframe_regex, value):
        raise ValidationError('HTML код містить некоректний URL або не є відео з YouTube.')


# ---- Відео -------------------
class Video(models.Model):
    sort_order = models.IntegerField(
        verbose_name="Номер відео", 
        help_text="Номер відео потрібен, щоб вивести відео в правильному порядку",
        default=1,
        null=False,
        blank=False,
        )
    title = models.CharField(
        verbose_name="Назва відео",
        max_length=255,
        unique=True,
        )
    video_author = models.ForeignKey(
        VideoAuthor,
        verbose_name="Канал, автор відео",
        on_delete=models.PROTECT,
        blank=False,
        )
    description = models.TextField(
        verbose_name="Опис відео",
        max_length=2000, 
        blank=True,
        )
    html_code = models.TextField(
        verbose_name="HTML код відео з youtube",
        max_length=2000,
        blank=True,
        unique=False,
        validators=[validate_html_code],
    )
    link = models.URLField(
        verbose_name="Посилання на відео",
        help_text= "Значення буде вибрано автоматично з попереднього поля при збереженні даних",
        max_length=255,
        blank=True,
        unique=True,
        editable=False
    )
    level = models.ForeignKey(
        Level,
        verbose_name="Рівень",
        help_text= "Рівень знань учня, на який розраховано відео",
        on_delete=models.PROTECT,
        blank=False,
        )  
    rating = models.DecimalField(
        verbose_name = "Оцінка відео",
        help_text= "Вкажіть оцінку від 0 до 12",
        max_digits=4, # Максимальна кількість цифр, включаючи десяткові
        decimal_places = 2, # Кількість цифр після десяткової коми
        default = 12,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(12),
        ],
        blank=False,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
        blank=True,
        )
    science = models.ForeignKey(
        Science,
        verbose_name="Наукова дисципліна",
        on_delete=models.PROTECT,
        blank=False,
        )
    text_book = models.ForeignKey(
        TextBook,
        verbose_name="Підручник",
        help_text= "Заповніть це поле, якщо в відео згадується певний підручник.",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    course = models.ForeignKey(
        GradeSubject,
        verbose_name="Клас-Предмет",
        help_text= "Заповніть це поле, якщо відео передбачено тільки для певного класу та предмету. Якщо відео можна використати для повторення в іншому класі, то вказувати Клас-Предмет не потрібно.",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        )
    is_active = models.BooleanField(
        verbose_name="Виводити",
        default=True,
        )
    slug = models.SlugField(
        verbose_name="slug",
        help_text="заповнюється автоматично",
        unique=True,
        blank=False,
        editable=False,
        max_length=255,
        )
    objects = models.Manager()  # для можливості створення запитів до БД

    def __str__(self):
        return self.title
    
    def save(self):
        url_pattern = re.compile(r'src="([^"]*)"')  # Регулярний вираз для виділення URL
        match = url_pattern.search(self.html_code)  # Знаходження URL за допомогою регулярного виразу

        if match:
            url = match.group(1)  # Отримання URL з відповідного групи
            print(url)
            self.link = url
        else:
            print("URL не знайдено")

        super(Video, self).save()

    class Meta:
        verbose_name = 'Навчальне відео'
        verbose_name_plural = '3. Відеотека'



# ---- Тема-Відео -------------------
class TopicVideo(models.Model):
    topic = models.ForeignKey(
        Topic,
        verbose_name="Тема",
        on_delete=models.PROTECT,
        )
    video = models.ForeignKey(
        Video,
        verbose_name="Відео",
        on_delete=models.PROTECT,
        )
    title = models.CharField(
        verbose_name="Тема-Відео",
        help_text="заповнюється автоматично",
        max_length=255,
        blank=True,
        unique=True,
        editable=False,
        )
    description = models.TextField(
        verbose_name="Опис до відео в рамках вибраної теми",
        max_length=2000, 
        blank=True,
        )
    is_active = models.BooleanField(
        verbose_name="Активно", 
        default=True,
        )
    sort_order = models.IntegerField(
        verbose_name="Порядок виводу", 
        help_text="Якщо поле залишиться пустим, то після збереженні елемент буде виводитися останнім.",
        null=True,
        blank=True,
        )
    objects = models.Manager()  # для можливості створення запитів до БД

    def __str__(self):
        return self.topic.title+' - '+self.video.title

    def save(self):
        self.title = f"{self.topic.chapter.course.title} - Розділ {self.topic.chapter.title} - Тема {self.topic.title} - Відео {self.video.title}"
        super(TopicVideo, self).save()

    class Meta:
        verbose_name = 'Тема-Відео'
        verbose_name_plural = '4. Тема-Відео'
        unique_together = ('topic', 'video')


@receiver(pre_save, sender=Science)
@receiver(pre_save, sender=GradeType)
@receiver(pre_save, sender=Grade)
@receiver(pre_save, sender=Subject)
@receiver(pre_save, sender=TopicVideo)
@receiver(pre_save, sender=Level)
@receiver(pre_save, sender=Tag)
def set_sort_order(sender, instance, **kwargs):
    if instance.sort_order is None:
        # Отримуємо максимальне значення sort_order для всіх записів
        max_sort_order = sender.objects.aggregate(max_sort_order=models.Max('sort_order'))['max_sort_order']
        # Якщо max_sort_order є None, то встановлюємо 1, інакше збільшуємо на 1
        instance.sort_order = max_sort_order + 1 if max_sort_order is not None else 1


@receiver(pre_save, sender=Grade)
@receiver(pre_save, sender=Subject)
@receiver(pre_save, sender=Science)
@receiver(pre_save, sender=Chapter)
@receiver(pre_save, sender=Topic)
@receiver(pre_save, sender=TextBook)
@receiver(pre_save, sender=TextBookAuthor)
@receiver(pre_save, sender=Tag)
@receiver(pre_save, sender=Video)
def set_slug(sender, instance, **kwargs):
    instance.slug = slugify(instance.title)
