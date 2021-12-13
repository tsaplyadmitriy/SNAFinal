import json
import os
from math import ceil
import logging

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()

import datetime

from celery import Celery
from celery.schedules import crontab
from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater
from telegram.constants import MAX_CAPTION_LENGTH

from account.database import (get_client_by_telegram,
                              get_survey_questions,
                              get_test_questions,
                              update_client_step, get_default_training, add_course_passed)
from account.models import Bot, Client, Course, CourseStep, Survey, Test, Training, TrainingStep

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
celery_app = Celery('main', include=['main.tasks'])
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()
celery_app.conf.timezone = settings.TIME_ZONE
celery_app.conf.broker_transport_options = {'visibility_timeout': 31540000}

INITIAL_STEP_UNDERSCORES = 3

logger = logging.getLogger(__name__)


@celery_app.task(acks_late=True)
def send_generic_message(
        bot_token: str,
        user: str,
        course: str,
        text: str = None,
        video: str = None,
        photo: str = None,
        file: str = None,
        survey: Survey = None,
        test: Test = None,

):
    """Send message to user from specific bot

    Args:
        bot_token: bot token from which message is sent.
        user: user id to get from db.
        course: id of course added
        text: message text.
        video: path to video, default to None.
        photo: path to image, default to None.
        file: path to file, default to None
        survey: Survey object, default to None.
        test: Test object, default to None.
    """
    client = Client.objects.get(telegram_id=user)

    updater = Updater(bot_token, request_kwargs={'read_timeout': 1000, 'connect_timeout': 1000})

    course_id, step_number, total_steps, step_type, \
    step_id, step_position = [i for i in client.current_steps[str(course)].split('_')]

    # if test is unfinished, adding default training
    if step_type == 'test' and step_position != 0:
        current_test = Test.objects.get(id=step_id)

        training = get_default_training(current_test)

        if training is not None:
            add_training(client.id, training.id)

    if text:
        step_id = photo
        course_step = CourseStep.objects.get(id=step_id)

        photo = CourseStep.objects.get(id=photo).text_message_image
        file = CourseStep.objects.get(id=file).text_message_file

        if photo:
            if len(text) > MAX_CAPTION_LENGTH:
                updater.bot.send_photo(
                    chat_id=user,
                    photo=photo,
                )
                updater.bot.send_message(chat_id=user, text=text)
            else:
                updater.bot.send_photo(
                    chat_id=user,
                    photo=photo,
                    caption=text
                )
        else:
            updater.bot.send_message(
                chat_id=user,
                text=text,
            )

        if file:
            updater.bot.send_document(
                chat_id=user,
                document=file
            )

        if course_step.test or course_step.survey:
            pass
        else:
            step_number = int(step_number) + 1

        client.current_steps[course] = str(course_id) + '_' + str(step_number) + '_' + total_steps + '_text_' + str(
            step_id) + '_' + step_position
        client.save()

        if int(step_number) == int(total_steps):
            add_course_passed(client, int(course_id))
    elif test:
        logging.debug('sending test')
        test = Test.objects.get(id=test)
        first_question = get_test_questions(test)[0]

        text = first_question.text
        photo = first_question.image

        answers = first_question.get_answers()

        buttons = [[] for i in range(ceil(len(answers) / 2))]

        for idx, answer in enumerate(answers):
            buttons[idx // 2].append(InlineKeyboardButton(answer[0], callback_data=answer[1]))

        answers = InlineKeyboardMarkup(buttons)

        if photo:
            if len(text) > MAX_CAPTION_LENGTH:
                updater.bot.send_photo(
                    chat_id=user,
                    photo=photo
                )
                updater.bot.send_message(
                    chat_id=user,
                    text=text,
                    reply_markup=answers
                )
            else:
                updater.bot.send_photo(
                    chat_id=user,
                    photo=photo,
                    caption=text,
                    reply_markup=answers
                )
        else:
            updater.bot.send_message(
                chat_id=user,
                text=text,
                reply_markup=answers
            )

        client.current_steps[course] = str(course_id) + '_' + str(
            int(step_number) + 1) + '_' + total_steps + '_test_' + str(test.id) + '_1'
        client.save()

    elif survey:
        survey = Survey.objects.get(id=survey)

        first_question = get_survey_questions(survey)[0]

        text = first_question.text
        image = first_question.image

        answers = first_question.get_answers()

        buttons = [[] for i in range(ceil(len(answers) / 2))]

        for idx, answer in enumerate(answers):
            buttons[idx // 2].append(InlineKeyboardButton(answer, callback_data=answer))

        answers = InlineKeyboardMarkup(buttons)

        logging.debug(image)

        if image:
            updater.bot.send_photo(
                chat_id=user,
                photo=image,
                caption=text,
                reply_markup=answers
            )
        else:
            updater.bot.send_message(
                chat_id=user,
                text=text,
                reply_markup=answers
            )

        client.current_steps[course] = str(course_id) + '_' + str(
            int(step_number) + 1) + '_' + total_steps + '_survey_' + str(survey.id) + '_1'
        client.save()
    else:
        step = CourseStep.objects.get(id=photo)
        logger.debug(step)
        logger.debug(step.text_message_image)

        if step.text_message_image:
            updater.bot.send_photo(
                chat_id=user,
                photo=step.text_message_image
            )
        elif step.text_message_file:
            updater.bot.send_document(
                chat_id=user,
                document=step.text_message_file
            )

        if step.test or step.survey:
            pass
        else:
            step_number = int(step_number) + 1

        client.current_steps[course] = str(course_id) + '_' + str(step_number) + '_' + total_steps + '_text_' + str(
            step_id) + '_' + step_position
        client.save()

        if int(step_number) == int(total_steps):
            add_course_passed(client, int(course_id))


@celery_app.task(acks_late=True)
def send_training_step(
        bot_token: str,
        client_telegram_id: str,
        training_step_id: str
):
    client = get_client_by_telegram(client_telegram_id)

    updater = Updater(bot_token)

    training_step = TrainingStep.objects.get(id=training_step_id)

    message = training_step.text + '\n' + training_step.video_url

    if training_step.image:
        updater.bot.send_photo(
            chat_id=client_telegram_id,
            photo=training_step.image,
            caption=message
        )
    else:
        updater.bot.send_message(
            chat_id=client_telegram_id,
            text=message
        )


def add_course(client_id, course_id):
    course = Course.objects.get(id=course_id)
    steps = course.steps.all()
    cli = Client.objects.get(id=client_id)

    if cli.is_tester:
        return

    new_step = str(course.id) + '_0_' + str(len(steps)) + '_'

    for step in steps:
        t = step.time
        e = datetime.datetime.now() + datetime.timedelta(days=step.day_number)
        # taking 3 hours from setting due to timezone issues and timezone being forward 3 hours
        e += datetime.timedelta(hours=-e.hour + t.hour - 3, minutes=-e.minute + t.minute,
                                seconds=-e.second + t.second, microseconds=-e.microsecond)

        logging.debug(e)
        if step.text_message:
            logging.debug(step.text_message)
            '''
            new step is used for tracking, where user is in the course,
            and when its initialized, it is in the form of <course_id>_0_<steps_amount>_,
            so if course was just started, we check if it is the first step, and change the value.
            the number of underscores is used to check that.
            '''
            if new_step.count('_') == INITIAL_STEP_UNDERSCORES:
                new_step += 'text_0_0'

            send_generic_message.apply_async(
                kwargs={
                    'bot_token': course.bot.token,
                    'user': cli.telegram_id,
                    'course': course.id,
                    'text': step.text_message,
                    'photo': step.id,
                    'file': step.id
                }, eta=e, retry=False)

        ''' 
        sometimes the order of messages get mixed up, and text is sent after test or survey,
        which causes the whole course logic to break,
        so in order to avoid race conditions, little delay before other steps introduced
        '''
        e += datetime.timedelta(seconds=2)

        if step.test:
            logging.debug(e)
            logging.debug(step.test)
            if new_step.count('_') == INITIAL_STEP_UNDERSCORES:
                new_step += 'test_' + str(step.test.id) + '_0'
            send_generic_message.apply_async(
                kwargs={
                    'bot_token': course.bot.token,
                    'user': cli.telegram_id,
                    'course': course.id,
                    'test': step.test.id,
                    'photo': step.id,
                }, eta=e)

        if step.survey:
            logging.debug(e)

            logging.debug(step.survey)
            if new_step.count('_') == INITIAL_STEP_UNDERSCORES:
                new_step += 'survey_' + str(step.survey.id) + '_0'
            send_generic_message.apply_async(
                kwargs={
                    'bot_token': course.bot.token,
                    'user': cli.telegram_id,
                    'course': course.id,
                    'survey': step.survey.id,
                    'photo': step.id,
                }, eta=e)
        if (step.text_message_image or step.text_message_file) and (not step.text_message):
            logging.debug(step)
            if new_step.count('_') == INITIAL_STEP_UNDERSCORES:
                new_step += 'text_0_0'
            send_generic_message.apply_async(
                kwargs={
                    'bot_token': course.bot.token,
                    'user': cli.telegram_id,
                    'course': course.id,
                    'photo': step.id,
                }, eta=e)

    logging.debug(new_step)
    if cli.current_steps is not None:
        cli.current_steps[course_id] = new_step
    else:
        cli.current_steps = {course_id: new_step}
    cli.save()


def add_training(client_id, training_id, bot_token):
    client = Client.objects.get(id=client_id)
    training = Training.objects.get(id=training_id)

    if client.is_tester:
        return

    for step in training.steps.all():
        t = step.time
        e = datetime.datetime.now() + datetime.timedelta(days=step.day_number)
        # taking 3 hours from setting due to timezone issues and timezone being forward 3 hours
        e += datetime.timedelta(hours=-e.hour + t.hour - 3, minutes=-e.minute + t.minute,
                                seconds=-e.second + t.second, microseconds=-e.microsecond)

        logging.debug(e)

        send_training_step.apply_async(kwargs={
            'bot_token': bot_token,
            'client_telegram_id': client.telegram_id,
            'training_step_id': step.id,
        }, eta=e, retry=False)

        logging.debug(step)
