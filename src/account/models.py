import datetime
import logging

from django.apps import apps
from django.contrib import auth
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models

logger = logging.getLogger(__name__)

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class Bot(models.Model):
    class Meta:
        verbose_name = 'Бот'
        verbose_name_plural = 'Боты'

    handle = models.TextField()
    current_port = models.IntegerField(null=True, blank=True)
    token = models.TextField(null=True)

    def __str__(self):
        return self.handle


class CourseCategory(models.Model):
    class Meta:
        verbose_name = 'Категория курсов'
        verbose_name_plural = 'Категории курсов'

    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name


class Course(models.Model):
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['course_number']

    bot = models.ForeignKey(Bot, on_delete=models.SET_NULL, null=True)
    name = models.TextField(max_length=100,default='')
    course_number = models.IntegerField(default=0)
    category = models.ForeignKey(CourseCategory, related_name='courses', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class CourseStep(models.Model):
    day_number = models.IntegerField()
    time = models.TimeField()
    test = models.ForeignKey("Test", models.CASCADE, "course_steps", null=True, blank=True)
    survey = models.ForeignKey("Survey", models.CASCADE, "course_steps", null=True, blank=True)
    text_message = models.TextField("course_steps", null=True, blank=True)
    text_message_image = models.ImageField(null=True, blank=True)
    text_message_file = models.FileField(null=True, blank=True)
    course = models.ForeignKey(Course, models.CASCADE, "steps")
    step_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ['step_order']

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        logger.debug(f'Saving course step id {self.id} with day {self.day_number}, time {str(self.time)} for course {self.course.name}')
        super(CourseStep, self).save()



class User(AbstractUser):
    objects = UserManager()

    REQUIRED_FIELDS = []


class Client(models.Model):
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    phone = models.TextField(max_length=12, unique=True)
    name = models.CharField(max_length=40, null=True, blank=True)
    handle = models.CharField(max_length=80, null=True)
    timezone = models.TextField(max_length=40, blank=True, null=True) # In form of Asia/Omsk
    telegram_id = models.IntegerField(blank=True, null=True, unique=True)

    # json field with data of type <course_id>: <course_step>
    # course_step description: <course_id>_<step_number>_<total_steps>_<step_type>_<step_id>_<position in step>
    current_steps = models.JSONField(blank=True, null=True)
    courses_passed = models.ManyToManyField(Course, blank=True, related_name='courses_passed', verbose_name='Пройденные курсы')
    current_courses = models.ManyToManyField(Course, blank=True, null=True, related_name='current_courses')
    previous_step = models.TextField(blank=True, null=True)
    is_tester = models.BooleanField(default=False)

    def __str__(self):
        return self.phone


class AccessCode(models.Model):
    class Meta:
        verbose_name = 'Код доступа'
        verbose_name_plural = 'Коды доступа'

    code = models.TextField(max_length=16, unique=True)
    is_active = models.BooleanField(default=True)
    course_category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.code


class Trainer(models.Model):
    class Meta:
        verbose_name = 'Тренер'
        verbose_name_plural = 'Тренеры'

    name = models.TextField(max_length=80)

    def __str__(self):
        return self.name


class Training(models.Model):
    class Meta:
        verbose_name = 'Тренировка'
        verbose_name_plural = 'Тренировки'

    name = models.CharField(max_length=100, null=True)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return 'Тренировка'


class TrainingStep(models.Model):
    class Meta:
        verbose_name = 'Шаг тренировки'
        verbose_name_plural = 'Шаги тренировок'
        ordering = ['step_order']

    day_number = models.IntegerField()
    time = models.TimeField()
    video_url = models.URLField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    training = models.ForeignKey(Training, models.CASCADE, "steps")
    step_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return self.text

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        logger.debug(f'Saving training step id {self.id} with day {self.day_number}, {str(self.time)} for course {self.training.name}')
        super(TrainingStep, self).save()


class TextMessage(models.Model):
    class Meta:
        verbose_name = 'Текстовое сообщение'

    header = models.CharField(max_length=200)
    text = models.TextField()
    image = models.ImageField(blank=True, null=True)
    file = models.FileField(blank=True, null=True)

    def __str__(self):
        return self.header


class Test(models.Model):
    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    name = models.CharField(max_length=100, default='Тест')

    def __str__(self):
        if self.name:
            return self.name
        else:
            return 'Тест'


class TestQuestion(models.Model):
    class Meta:
        verbose_name = 'Вопрос к тесту'
        verbose_name_plural = 'Вопросы к тесту'
        ordering = ['step_order']

    text = models.TextField()
    test = models.ForeignKey(Test, on_delete=models.CASCADE, null=True)
    image = models.ImageField(blank=True, null=True)
    answer_1 = models.CharField(max_length=100, blank=True, null=True)
    answer_1_weight = models.IntegerField(blank=True, null=True)

    answer_2 = models.CharField(max_length=100, blank=True, null=True)
    answer_2_weight = models.IntegerField(blank=True, null=True)

    answer_3 = models.CharField(max_length=100, blank=True, null=True)
    answer_3_weight = models.IntegerField(blank=True, null=True)

    answer_4 = models.CharField(max_length=100, blank=True, null=True)
    answer_4_weight = models.IntegerField(blank=True, null=True)

    answer_5 = models.CharField(max_length=100, blank=True, null=True)
    answer_5_weight = models.IntegerField(blank=True, null=True)

    answer_6 = models.CharField(max_length=100, blank=True, null=True)
    answer_6_weight = models.IntegerField(blank=True, null=True)

    step_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # images = self.images_field
        super(TestQuestion, self).save()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        logger.debug(f'Saving test question id {self.id} with text {self.text} for test {self.test.name}')
        super(TestQuestion, self).save()

    def __str__(self):
        if self.text:
            return self.text
        else:
            return 'Question'

    def get_answers(self):
        all_answers = []

        if self.answer_1:
            all_answers.append((self.answer_1, self.answer_1_weight))

        if self.answer_2:
            all_answers.append((self.answer_2, self.answer_2_weight))

        if self.answer_3:
            all_answers.append((self.answer_3, self.answer_3_weight))

        if self.answer_4:
            all_answers.append((self.answer_4, self.answer_4_weight))

        if self.answer_5:
            all_answers.append((self.answer_5, self.answer_5_weight))

        if self.answer_6:
            all_answers.append((self.answer_6, self.answer_6_weight))

        return all_answers


class TestEvent(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, null=True)
    threshold = models.IntegerField()
    meaning = models.TextField(blank=True, null=True)
    meaning_photo = models.ImageField(blank=True, null=True)
    training = models.ManyToManyField(Training, blank=True)
    step_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ['step_order']

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        logger.debug(f'Saving test event id {self.id} with threshold {str(self.threshold)} for test {self.test.name}')
        super(TestEvent, self).save()


class TestResult(models.Model):
    class Meta:
        verbose_name = 'Результат теста'
        verbose_name_plural = 'Результаты теста'

    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    user = models.ForeignKey(Client, on_delete=models.CASCADE)
    result = models.IntegerField(default=0)


class Survey(models.Model):
    class Meta:
        verbose_name = 'Опрос'
        verbose_name_plural = 'Опросы'

    name = models.TextField(null=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return 'Опрос'


class SurveyQuestion(models.Model):
    class Meta:
        verbose_name = 'Вопрос опроса'
        verbose_name_plural = 'Вопросы опросов'
        ordering = ['step_order']

    text = models.TextField()
    image = models.ImageField(blank=True, null=True)
    survey = models.ForeignKey(Survey, null=True, on_delete=models.CASCADE)

    answer_1 = models.CharField(max_length=100, blank=True, null=True)

    answer_2 = models.CharField(max_length=100, blank=True, null=True)

    answer_3 = models.CharField(max_length=100, blank=True, null=True)

    answer_4 = models.CharField(max_length=100, blank=True, null=True)

    answer_5 = models.CharField(max_length=100, blank=True, null=True)

    answer_6 = models.CharField(max_length=100, blank=True, null=True)
    step_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    def __str__(self):
        if self.text:
            return self.text
        else:
            return 'Test'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        logger.debug(f'Saving survey question id {self.id} with text {self.text} for surver {self.survey.name}')
        super(SurveyQuestion, self).save()

    def get_answers(self):
        all_answers = []

        if self.answer_1:
            all_answers.append(self.answer_1)

        if self.answer_2:
            all_answers.append(self.answer_2)

        if self.answer_3:
            all_answers.append(self.answer_3)

        if self.answer_4:
            all_answers.append(self.answer_4)

        if self.answer_5:
            all_answers.append(self.answer_5)

        if self.answer_6:
            all_answers.append(self.answer_6)

        return all_answers


class SurveyUserAnswer(models.Model):
    class Meta:
        verbose_name = 'Пользовательский ответ на вопрос'
        verbose_name_plural = 'Пользовательские ответы на опросы'

    user = models.ForeignKey(Client, on_delete=models.CASCADE)
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    answer = models.TextField()