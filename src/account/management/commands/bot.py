import os

from django.core.management import BaseCommand
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                    ReplyKeyboardRemove)
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageFilter,
                          MessageHandler, Updater)

from ...database import (add_user_data, is_access_code_exists, get_course, get_bot_by_course_id,
                         is_user_exists_by_phone)
from ...utils import get_server_time
from .resources.yaml_reader import YamlReader

RESOURCE_FILE = 'main_bot_messages.yaml'
reader = YamlReader(RESOURCE_FILE)

class CodeFilter(MessageFilter):
    def filter(self, message):
        return is_access_code_exists(message.text)

code_filter = CodeFilter()

# load_dotenv()

TOKEN = os.getenv('MAIN_BOT', default='1997483730:AAEEa36JmT__biB-8wHe3i_9b7d2KfpuAcY') # dummy bot token for local testing
updater = Updater(TOKEN, use_context=True)

FIRST_BUY, NEW_USER, OLD_USER, NEW_USER_PHONE, NEW_USER_TIMEZONE, \
NEW_USER_LINK, NEW_USER_SUCCESS, NEW_USER_LINK_2, NEW_USER_LINK_3, \
NEW_USER_LINK_4, NEW_USER_PRIVACY, OLD_USER_PHONE, OLD_USER_PHONE_CHECK_FAIL = range(13)

TWO_DAYS = 2 * 24 * 60 * 60
THREE_DAYS = 3 * 24 * 60 * 60
FIFTEEN_MINUTES = 15 * 60


def remind_timezone_after_two_days(context):
    job = context.job
    context.bot.send_message(job.context, text=reader.get('TIMEZONE_REMIND_TWO_DAYS'))


def remind_timezone_after_three_days(context):
    job = context.job
    context.bot.send_message(job.context, text=reader.get('TIMEZONE_REMIND_THREE_DAYS'))


def remind_access_code_after_fifteen_minutes(context):
    job = context.job
    context.bot.send_message(job.context, text=reader.get('ACCESS_CODE_REMIND'))


def remove_job_if_exists(name: str, context) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def start(update, context):
    context.user_data.clear()
    context.user_data['telegram_id'] = update.message.from_user['id']
    context.user_data['handle'] = '@' + update.message.from_user['username']

    update.message.reply_text(reader.get('HELLO_MESSAGE'), reply_markup=ReplyKeyboardRemove())

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(reader.get('FIRST_TIME_CHOICE'), callback_data='first_time')],
        [InlineKeyboardButton(reader.get('OLD_USER_CHOICE'), callback_data='old_user')]],
        resize_keyboard=True)
    update.message.reply_text(reader.get('FIRST_BUY_QUESTION'), reply_markup=keyboard)
    return FIRST_BUY


def error(update, context):
    update.message.reply_text(reader.get('FALLBACK_MESSAGE'))


def new_user_name(update, context):
    query = update.callback_query
    query.answer()

    query.message.reply_text(reader.get('NAME_QUESTION'))
    return NEW_USER


def old_user_phone(update, context):
    query = update.callback_query
    query.answer()
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(reader.get('FIRST_STEP_BUTTON'), callback_data='first_step')]])

    query.message.reply_text(reader.get('OLD_USER_PHONE_MESSAGE'))
    return OLD_USER


def new_user_phone(update, context):
    context.user_data['name'] = update.message.text
    update.message.reply_text(reader.get('NEW_USER_PHONE_MESSAGE'))
    return NEW_USER_PHONE


def correct_phone(update, context):
    context.user_data['phone'] = update.message.text
    update.message.reply_text(reader.get('TIMEZONE_MESSAGE'))

    context.job_queue.run_once(
        remind_timezone_after_two_days,
        TWO_DAYS,
        context=update.message.chat_id,
        name=str(update.message.chat_id) + '_tz_first')
    context.job_queue.run_once(
        remind_timezone_after_three_days,
        THREE_DAYS,
        context=update.message.chat_id,
        name=str(update.message.chat_id) + '_tz_second')

    return NEW_USER_TIMEZONE


def incorrect_phone(update, context):
    update.message.reply_text(reader.get('INCORRECT_PHONE_FORMAT_MESSAGE'))
    return NEW_USER_PHONE


def correct_timezone(update, context):
    context.user_data['timezone'] = get_server_time(update.message.text)

    remove_job_if_exists(str(update.message.chat_id) + '_tz_first', context)
    remove_job_if_exists(str(update.message.chat_id) + '_tz_second', context)
    context.job_queue.run_once(
        remind_access_code_after_fifteen_minutes,
        FIFTEEN_MINUTES,
        context=update.message.chat_id,
        name=str(update.message.chat_id) + '_code'
    )

    update.message.reply_text(reader.get('ACCESS_CODE_INPUT_MESSAGE'))

    return NEW_USER_LINK


def incorrect_timezone(update, context):
    update.message.reply_text(reader.get('INCORRECT_TIMEZONE_MESSAGE'))
    return NEW_USER_TIMEZONE


def correct_link(update, context):
    context.user_data['code'] = update.message.text
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(reader.get('BEFORE_START_READY'), callback_data='ready')]])

    remove_job_if_exists(str(update.message.chat_id) + '_code', context)

    update.message.reply_text(reader.get('BEFORE_START_MESSAGE'), reply_markup=keyboard)
    return NEW_USER_SUCCESS


def incorrect_link(update, context):
    update.message.reply_text(reader.get('INCORRECT_ACCESS_CODE_FIRST_MESSAGE'))
    return NEW_USER_LINK_2


def incorrect_link_2(update, context):
    update.message.reply_text(reader.get('INCORRECT_ACCESS_CODE_SECOND_MESSAGE'))

    return NEW_USER_LINK_3


def incorrect_link_3(update, context):
    update.message.reply_text(reader.get('INCORRECT_ACCESS_CODE_THIRD_MESSAGE'))

    return NEW_USER_LINK_4


def final_user_data(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_reply_markup(None)

    query.message.reply_text(reader.get('SUPPORT_MESSAGE'))

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(reader.get('READY_MESSAGE'), callback_data='accept_privacy')],
        [InlineKeyboardButton(reader.get('QUESTIONS_MESSAGE'), callback_data='ask_questions')]
    ])

    query.message.reply_text(reader.get('PROGRAM_START_MESSAGE'), reply_markup=keyboard)

    return NEW_USER_PRIVACY


def send_support_link(update, context):
    update.message.reply_text(reader.get('SUPPORT_LINK'))


def send_instagram_link(update, context):
    update.message.reply_text(reader.get('INSTAGRAM_LINK'))


def send_bot_link(update, context):
    query = update.callback_query
    query.answer()
    query.message.reply_text(reader.get('BEFORE_SENDING_BOT_LINK_MESSAGE'))
    # update_code(context.user_data['code'])
    course = get_course(context.user_data['code'], context.user_data['telegram_id'])
    del context.user_data['code']
    client_id = add_user_data(**context.user_data, course=course)

    bot_handle = get_bot_by_course_id(course.id)

    query.message.reply_text(bot_handle)
    return -1


def send_support_link_callback(update, context):
    query = update.callback_query
    query.answer()

    query.message.reply_text(reader.get('SUPPORT_LINK'))


def start_old_user(update, context):
    query = update.callback_query
    query.answer()

    query.message.reply_text(reader.get('HELLO_MESSAGE'), reply_markup=ReplyKeyboardRemove())

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(reader.get('FIRST_TIME_CHOICE'), callback_data='first_time')],
        [InlineKeyboardButton(reader.get('OLD_USER_CHOICE'), callback_data='old_user')]],
        resize_keyboard=True)
    query.message.reply_text(reader.get('FIRST_BUY_QUESTION'), reply_markup=keyboard)
    return FIRST_BUY


def old_user_phone(update, context):
    query = update.callback_query
    query.answer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(reader.get('FIRST_STEP_BUTTON'), callback_data='first_step')]
    ])

    query.edit_message_text(reader.get('OLD_USER_PHONE_MESSAGE'), reply_markup=keyboard)
    return OLD_USER_PHONE


def correct_phone_old_user(update, context):
    if is_user_exists_by_phone(update.message.text):
        context.user_data['phone'] = update.message.text
        update.message.reply_text(reader.get('TIMEZONE_MESSAGE'))
        return NEW_USER_TIMEZONE
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(reader.get('OLD_USER_ANOTHER_PHONE'), callback_data='another_phone')],
            [InlineKeyboardButton(reader.get('FIRST_STEP_BUTTON'), callback_data='first_step')]
        ])
        update.message.reply_text(reader.get('OLD_USER_NO_PHONE_MESSAGE'), reply_markup=keyboard)
        return OLD_USER_PHONE_CHECK_FAIL


def incorrect_phone_old_user(update, context):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(reader.get('FIRST_STEP_BUTTON'), callback_data='first_step')]
    ])

    update.message.reply_text(
        reader.get('INCORRECT_PHONE_FORMAT_MESSAGE'),
        reply_markup=keyboard
    )
    return OLD_USER_PHONE


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        FIRST_BUY: [
            CallbackQueryHandler(final_user_data, pattern='first_time'),
            CallbackQueryHandler(old_user_phone, pattern='old_user')
        ],
        NEW_USER: [
            MessageHandler(Filters.text, new_user_phone),
            CallbackQueryHandler(start_old_user, pattern='first_step'),
        ],
        NEW_USER_PHONE: [
            CallbackQueryHandler(start_old_user, pattern='first_step'),
            MessageHandler(Filters.regex('^(\+7)(\d{10})$'), correct_phone),
            MessageHandler(Filters.text, incorrect_phone),
        ],
        NEW_USER_TIMEZONE: [
            CallbackQueryHandler(start_old_user, pattern='first_step'),
            MessageHandler(Filters.regex(r'^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$'), correct_timezone),
            MessageHandler(Filters.text, incorrect_timezone),
        ],
        NEW_USER_LINK: [
            CommandHandler('start', start),
            CallbackQueryHandler(start_old_user, pattern='first_step'),
            MessageHandler(Filters.regex('^(\d{11})$') & code_filter, correct_link),
            MessageHandler(Filters.text, incorrect_link),
        ],
        NEW_USER_LINK_2: [
            CommandHandler('start', start),
            CallbackQueryHandler(start_old_user, pattern='first_step'),
            MessageHandler(Filters.regex('^(\d{11})$') & code_filter, correct_link),
            MessageHandler(Filters.text, incorrect_link_2),
        ],
        NEW_USER_LINK_3: [
            CommandHandler('start', start),
            CallbackQueryHandler(start_old_user, pattern='first_step'),
            MessageHandler(Filters.regex('^(\d{11})$') & code_filter, correct_link),
            MessageHandler(Filters.text, incorrect_link_3),
        ],
        NEW_USER_LINK_4: [
            CommandHandler('start', start),
            CallbackQueryHandler(start_old_user, pattern='first_step'),
            MessageHandler(Filters.regex('^(\d{11})$') & code_filter, correct_link),
            MessageHandler(Filters.regex('Служба заботы'), send_support_link),
            MessageHandler(Filters.regex('Наш Instagram'), send_instagram_link),
            MessageHandler(Filters.text, incorrect_link_3),
        ],
        NEW_USER_SUCCESS: [
            CommandHandler('start', start),
            CallbackQueryHandler(send_bot_link, pattern='ready'),
            MessageHandler(Filters.text, send_bot_link),
        ],
        NEW_USER_PRIVACY: [
            CommandHandler('start', start),
            CallbackQueryHandler(new_user_name, pattern='accept_privacy'),
            CallbackQueryHandler(send_support_link_callback, pattern='ask_questions'),
            CommandHandler('helpbot', send_support_link),
            CommandHandler('instagram', send_instagram_link),
        ],
        OLD_USER_PHONE: [
            CommandHandler('start', start),
            CallbackQueryHandler(start_old_user, pattern='first_step'),
            MessageHandler(Filters.regex('(\+7)(\d{10})'), correct_phone_old_user),
            MessageHandler(Filters.text, incorrect_phone_old_user),
        ],
        OLD_USER_PHONE_CHECK_FAIL: [
            CommandHandler('start', start),
            CallbackQueryHandler(start_old_user, pattern='first_step'),
            CallbackQueryHandler(old_user_phone, pattern='another_phone'),
        ]
    },
    fallbacks=[CommandHandler('start', start), MessageHandler(Filters.text, error)],
)


def start_main_bot():
        TOKEN = os.getenv('MAIN_BOT',
                          default='1997483730:AAEEa36JmT__biB-8wHe3i_9b7d2KfpuAcY')  # dummy bot token for local testing
        updater = Updater(TOKEN, use_context=True)

        updater.dispatcher.add_handler(conv_handler)
        updater.dispatcher.add_handler(CommandHandler('helpbot', send_support_link))
        updater.dispatcher.add_handler(CommandHandler('instagram', send_instagram_link))

        updater.start_webhook(
            listen='0.0.0.0',
            port=5000,
            url_path='/bot/' + TOKEN,
            webhook_url= 'https://' + os.getenv('HOSTNAME', '') + '/bot/' + TOKEN,
        )


class Command(BaseCommand):
    def handle(self, *args, **options):
        updater.dispatcher.add_handler(conv_handler)
        updater.dispatcher.add_handler(CommandHandler('helpbot', send_support_link))
        updater.dispatcher.add_handler(CommandHandler('instagram', send_instagram_link))


        updater.start_webhook(
            listen='0.0.0.0',
            port=5000,
            url_path='/bot/' + TOKEN,
            webhook_url='https://bot.qeep.life/bot/' + TOKEN,
        )


