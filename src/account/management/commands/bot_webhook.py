import datetime
import os
from time import sleep
import logging
from math import ceil
from enum import Enum

from django.core.management import BaseCommand
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater)

from main.celery import add_course, add_training, send_generic_message

from ...database import (get_bots, get_client_by_telegram, get_closest_test_event,
                         get_survey_by_id, get_survey_questions, get_test_by_id,
                         get_test_questions, insert_user_answer, update_bot_port,
                         update_client_step, get_trainers, get_training, add_course_passed, get_bot_by_token, get_client_course_by_bot)
from .bot import start_main_bot
from .resources.yaml_reader import YamlReader
from ...const import StepType

RESOURCE_FILE = 'main_bot_messages.yaml'
reader = YamlReader(RESOURCE_FILE)

STARTING_PORT = int(os.getenv('WEBHOOK_START_PORT'))

logger = logging.getLogger(__name__)
logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)


# TODO: REVISE IT AND OPTIMIZE IT
def process_message(update, context):
    client = get_client_by_telegram(update.message.from_user['id'])
    bot = get_bot_by_token(context.bot.token)

    course = get_client_course_by_bot(client, bot)

    if str(course.id) in client.current_steps.keys():
        course_id, step_number, total_steps, step_type, \
        step_id, step_position = [i for i in client.current_steps[str(course.id)].split('_')]

        # TODO: review and simplify logic behind this
        if step_type == StepType.TEST.value:
            update.message.reply_text('Выбери вариант!')
        elif step_type == StepType.SURVEY.value:
            survey = get_survey_by_id(int(step_id))

            all_questions = get_survey_questions(survey)

            previous_question = all_questions[int(step_position) - 1]
            answer = update.message.text
            insert_user_answer(client, survey, previous_question, answer)

            if len(all_questions) <= int(step_position):
                if int(step_number) == int(total_steps):
                    add_course_passed(client, int(course_id))
                update.message.reply_text('Ты прошел все, молодец!')
                return
            else:
                current_question = all_questions[int(step_position)]

            text = current_question.text

            answers = current_question.get_answers()
            image = current_question.image

            buttons = [[] for i in range(ceil(len(answers)/2))]

            for idx, answer in enumerate(answers):
                buttons[idx // 2].append(InlineKeyboardButton(answer, callback_data=answer))

            answers = InlineKeyboardMarkup(buttons)

            if image:
                update.message.reply_photo(
                    photo=image,
                    caption=text,
                    reply_markup=answers
                )
            else:
                update.message.reply_text(
                    text=text,
                    reply_markup=answers
                )

            new_step = course_id + '_' + step_number + '_' + total_steps + '_' + step_type + '_' + step_id + '_' + str(
                int(step_position) + 1)
            update_client_step(client, course, new_step)
        else:
            update.message.reply_text('Следующий шаг программы ждет тебя, но чуть позже!')
    else:
        update.message.reply_text('Привет! Следующий шаг программы еще не начался,'
                                  ' я сразу напишу тебе как только он начнется!')


def process_query_callback(update, context):
    query = update.callback_query
    query.answer()

    client = get_client_by_telegram(query.from_user['id'])
    bot = get_bot_by_token(context.bot.token)

    course = get_client_course_by_bot(client, bot)

    if str(course.id) in client.current_steps.keys():
        course_id, step_number, total_steps, step_type,\
        step_id, step_position = [i for i in client.current_steps[str(course.id)].split('_')]

        # TODO: review and simplify logic behind this
        if step_type == StepType.TEST.value:
            if 'score' in context.user_data:
                context.user_data['score'] += int(update.callback_query.data)
            else:
                context.user_data['score'] = int(update.callback_query.data)

            test = get_test_by_id(int(step_id))

            all_questions = get_test_questions(test)

            if len(all_questions) <= int(step_position):
                if int(step_number) == int(total_steps):
                    add_course_passed(client, int(course_id))
                event = get_closest_test_event(test, context.user_data['score'])
                context.user_data['score'] = 0
                if event.meaning:
                    if event.meaning_photo:
                        if len(event.meaning) > 1024:
                            query.message.reply_photo(event.meaning_photo)
                            query.message.reply_text(event.meaning)
                        else:
                            query.message.reply_photo(photo=event.meaning_photo, caption=event.meaning)
                    else:
                        query.message.reply_text(event.meaning)
                if event.training:
                    trainers = get_trainers(event)

                    if len(trainers) > 0:
                        buttons = [[] for i in range(ceil(len(trainers)/2))]

                        for idx, trainer in enumerate(trainers):
                            buttons[idx//2].append(InlineKeyboardButton(trainer.name, callback_data=trainer.name))

                        keyboard = InlineKeyboardMarkup(buttons)

                        query.message.reply_text('С кем бы ты хотел тренироваться?', reply_markup=keyboard)

                        context.user_data['event_id'] = event.id

                        new_step = course_id + '_' + step_number + '_' + total_steps + '_trainer_0_0'
                        update_client_step(client, course, new_step)


                return
            else:
                current_question = all_questions[int(step_position)]

            text = current_question.text
            photo = current_question.image

            answers = current_question.get_answers()

            buttons = [[] for i in range(ceil(len(answers) / 2))]

            for idx, answer in enumerate(answers):
                buttons[idx // 2].append(InlineKeyboardButton(answer[0], callback_data=answer[1]))

            answers = InlineKeyboardMarkup(buttons)

            if photo:
                if len(text) > 1024:
                    query.message.reply_photo(photo)
                    query.message.reply_text(
                        text=text,
                        reply_markup=answers
                    )
                else:
                    query.message.reply_photo(
                        photo=photo,
                        caption=text,
                        reply_markup=answers
                    )
            else:
                query.message.reply_text(
                    text=text,
                    reply_markup=answers
                )

            new_step = course_id + '_' + step_number + '_' + total_steps + '_' + step_type + '_' + step_id + '_' + str(
                int(step_position) + 1)
            update_client_step(client, course, new_step)
        elif step_type == StepType.SURVEY.value:
            survey = get_survey_by_id(int(step_id))

            all_questions = get_survey_questions(survey)

            previous_question = all_questions[int(step_position)-1]
            answer = update.callback_query.data
            insert_user_answer(client, survey, previous_question, answer)

            if len(all_questions) <= int(step_position):
                if int(step_number) == int(total_steps):
                    add_course_passed(client, int(course_id))
                query.message.reply_text('Ты прошел все, молодец!')
                return
            else:
                current_question = all_questions[int(step_position)]

            text = current_question.text
            image = current_question.image

            answers = current_question.get_answers()

            buttons = [[] for i in range(ceil(len(answers) / 2))]

            for idx, answer in enumerate(answers):
                buttons[idx // 2].append(InlineKeyboardButton(answer, callback_data=answer))

            answers = InlineKeyboardMarkup(buttons)

            if image:
                query.message.reply_photo(
                    photo=image,
                    caption=text,
                    reply_markup=answers
                )
            else:
                query.message.reply_text(
                    text=text,
                    reply_markup=answers
                )

            new_step = course_id + '_' + step_number + '_' + total_steps + '_' + step_type + '_' + step_id + '_' + str(
                int(step_position) + 1)
            update_client_step(client, course, new_step)
        elif step_type == StepType.TRAINING.value:
            trainer_name = update.callback_query.data

            training = get_training(trainer_name, context.user_data['event_id'])

            add_training(client.id, training.id, bot.token)

            query.edit_message_reply_markup(None)

            query.message.reply_text(
                'Ты записался на тренировку к: ' + trainer_name + '. Тебе будут приходить тренировки от этого тренера.',
                reply_markup=None

            )

        else:
            query.message.reply_text('Следующий шаг программы ждет тебя, но чуть позже!')
    else:
        query.message.reply_text('Привет! Следующий шаг программы еще не начался,'
                                  ' я сразу напишу тебе как только он начнется!')


def subscribe_to_course(update, context):
    client = get_client_by_telegram(update.message.from_user['id'])
    bot = get_bot_by_token(context.bot.token)

    course = get_client_course_by_bot(client, bot)

    if course is not None and client.current_steps is not None and str(course.id) in client.current_steps.keys():
        update.message.reply_text('Ты уже проходишь этот курс! Некуда спешить!')
        return

    if course in client.current_courses.all():
        add_course(client.id, course.id)

        first_step = course.steps.all()[0]

        if first_step.day_number != 0:
            first_step_time = first_step.time.strftime('%H:%M')

            update.message.reply_text(f'Привет! 👋🏻 Курс стартует завтра в {first_step_time}. Ты получишь своё первое '
                                      f'уведомление 😉')
    else:
        update.message.reply_text('forbidden')


def send_support_bot(update, context):
    update.message.reply_text(reader.get('SUPPORT_LINK'))


def send_instagram_link(update, context):
    update.message.reply_text(reader.get('INSTAGRAM_LINK'))


def call_next_step(update, context):
    user_telegram_id = update.message.from_user['id']

    logger.debug(user_telegram_id)

    client = get_client_by_telegram(user_telegram_id)
    bot = get_bot_by_token(context.bot.token)
    bot_token = context.bot.token

    course = get_client_course_by_bot(client, bot)

    if not client.is_tester:
        return

    if not client.current_steps:
        client.current_steps = {}
        client.save()

    if str(course.id) not in client.current_steps.keys():
        first_step = course.steps.all()[0]

        update.message.reply_text(f'Уведомление {first_step.day_number} день в {str(first_step.time)}')

        if first_step.text_message:
            client.current_steps[str(course.id)] = str(course.id) + '_0_' + str(len(course.steps.all())) + '_text_' + \
                                  str(first_step.id) + '_0'
            client.save()

            send_generic_message(bot_token=bot_token,
                                 user=client.telegram_id,
                                 text=first_step.text_message,
                                 course=course.id,
                                 photo=first_step.id,
                                 file=first_step.id)

        if first_step.test:
            client.current_steps[str(course.id)] = str(course.id) + '_0_' + str(len(course.steps.all())) + '_test_' + \
                                  str(first_step.test.id) + '_0'
            client.save()

            send_generic_message(bot_token=bot_token,
                                 user=client.telegram_id,
                                 course=course.id,
                                 test=first_step.test.id)

        if first_step.survey:
            client.current_steps[str(course.id)] = str(course.id) + '_0_' + str(len(course.steps.all())) + '_survey_' + \
                                  str(first_step.survey.id) + '_0'
            client.save()

            send_generic_message(bot_token=bot_token,
                                 user=client.telegram_id,
                                 course=course.id,
                                 survey=first_step.survey.id)

        if (first_step.text_message_image or first_step.text_message_file) and (not first_step.text_message):
            client.current_steps[str(course.id)] = str(course.id) + '_0_' + str(len(course.steps.all())) + '_text_' + \
                                  str(first_step.id) + '_0'
            client.save()
            send_generic_message(bot_token=bot_token,
                                 user=client.telegram_id,
                                 course=course.id,
                                 photo=first_step.id)

        return

    course_id, step_number, total_steps, step_type,\
    step_id, step_position = [i for i in client.current_steps[str(course.id)].split('_')]

    if int(step_number) >= int(total_steps):
        update.message.reply_text('Шаги закончились')
        return

    current_step = course.steps.all()[int(step_number)]

    update.message.reply_text(f'Уведомление {current_step.day_number} день в {str(current_step.time)}')

    if current_step.text_message:
        send_generic_message(bot_token=bot_token,
                             user=client.telegram_id,
                             course=course.id,
                             text=current_step.text_message,
                             photo=current_step.id,
                             file=current_step.id)

    if current_step.test:
        send_generic_message(bot_token=bot_token,
                             user=client.telegram_id,
                             course=course.id,
                             test=current_step.test.id)

    if current_step.survey:
        send_generic_message(bot_token=bot_token,
                             user=client.telegram_id,
                             course=course.id,
                             survey=current_step.survey.id)

    if (current_step.text_message_image or current_step.text_message_file) and (not current_step.text_message):
        send_generic_message(bot_token=bot_token,
                             user=client.telegram_id,
                             course=course.id,
                             photo=current_step.id)


def start_bot(bot, idx):
    logger.debug(f'starting {bot.handle} on port {STARTING_PORT+idx}')
    logger.debug(os.getenv('HOSTNAME', ''))
    updater = Updater(bot.token)

    updater.dispatcher.add_handler(CommandHandler('start', subscribe_to_course))
    updater.dispatcher.add_handler(CommandHandler('helpbot', send_support_bot))
    updater.dispatcher.add_handler(CommandHandler('instagram', send_instagram_link))
    updater.dispatcher.add_handler(CommandHandler('next', call_next_step))
    updater.dispatcher.add_handler(MessageHandler(~Filters.regex(r'^\d*\.?,?\d*$') & ~Filters.command, process_message))
    updater.dispatcher.add_handler(CallbackQueryHandler(process_query_callback, pattern=r'^(?!CBT_).*'))

    updater.start_webhook(
        listen='0.0.0.0',
        port=STARTING_PORT + idx,
        url_path='/bot/' + bot.token,
        webhook_url='https://' + os.getenv('HOSTNAME', '') + '/bot/' + bot.token
    )

    update_bot_port(bot, STARTING_PORT+idx)

    return bot


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.debug(os.getenv('HOSTNAME'))
        start_main_bot()
        logger.debug('started main bot on 5000')

        bots_started = ['@qeep_main_bot']

        while True:

            bots = get_bots()

            for idx, bot in enumerate(bots):
                if bot.handle.strip() in bots_started:
                    continue

                bot = start_bot(bot, len(bots_started)-2)
                logger.debug(f'{bot.handle} started on port {STARTING_PORT+len(bots_started)-2}')
                bots_started.append(bot.handle)

            sleep(30)
