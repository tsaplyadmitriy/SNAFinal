import os
from typing import List, Optional

from django.core.files import File

from .models import *


def is_user_exists_by_phone(phone: str) -> bool:
    user = Client.objects.filter(phone=phone).count()

    if user:
        return True
    else:
        return False


def is_user_exists_by_telegram_id(telegram_id: str) -> bool:
    user = Client.objects.filter(telegram_id=telegram_id).count()

    if user:
        return True
    else:
        return False


def is_access_code_exists(code: str) -> bool:
    code = AccessCode.objects.filter(code=code, is_active=True)

    if code:
        return True
    else:
        return False


def update_code(code):
    code = AccessCode.objects.get(code=code)
    code.is_active = False
    code.save()


def get_course(code: str, telegram_id: str) -> Course:
    code = AccessCode.objects.get(code=code)

    courses = list(code.course_category.courses.all().order_by('course_number'))

    if Client.objects.filter(telegram_id=telegram_id).exists():
        user_courses = list(Client.objects.get(telegram_id=telegram_id).courses_passed.all())

        for user_course in user_courses:
            if user_course in courses:
                courses.remove(user_course)

    if len(courses) > 0:
        return courses[0]
    else:
        return None


def get_bot_by_course_id(course_id: int) -> str:
    course = Course.objects.get(id=course_id)

    return course.bot.handle


def add_user_data(
        phone: str,
        handle: str,
        telegram_id: str,
        course: Course,
        name: str = '',
        timezone: str = '',
) -> int:
    print(course)
    if is_user_exists_by_phone(phone):
        user = Client.objects.get(phone=phone)
        user.handle = handle
        user.telegram_id = telegram_id
        user.current_courses.add(course)
        user.current_steps = {}
        user.save()
    else:
        user = Client(phone=phone, name=name, handle=handle, telegram_id=telegram_id, timezone=timezone)
        user.save()
        user.current_courses.add(course)
        user.save()

        if not user.current_steps:
            user.current_steps = {}
            user.save()

    return user.id


def is_bot_exists_by_handle(handle: str) -> bool:
    """Check if bot exists in database using handle from telegram user.

    Args:
        handle (str): telegram handle of bot.

    Returns:
        True or False.
    """
    bot = Bot.objects.filter(handle=handle).count()

    if bot:
        return True
    else:
        return False


def add_ticket(data: dict) -> int:
    """Add ticket on specific bot

    Args:
        data: user_id, bot, ticket text, image
    """
    if 'image' in data:
        data['image'][1].download(data['image'][0] + '.jpg')

        image_path = data['image'][0] + '.jpg'

        data['image'] = File(open(data['image'][0] + '.jpg', 'rb'))
    else:
        data['image'] = None

    client = Client.objects.filter(telegram_id=data['user_id'])

    if data['bot_error'] is not None:
        data['bot_error'] = Ticket.BOT_PROBLEM_TYPES[data['bot_error']][0]

    if len(client):
        ticket = Ticket(
            client=client[0],
            telegram_id=data['user_id'],
            problem_type=Ticket.PROBLEM_TYPES[data['type']][0],
            bot_problem_type=data['bot_error']
        )
    else:
        ticket = Ticket(
            telegram_id=data['user_id'],
            problem_type=Ticket.PROBLEM_TYPES[data['type']][0],
            bot_problem_type=data['bot_error']
        )

    ticket.save()

    ticket_message = TicketMessage(
        ticket=ticket,
        message_type=TicketMessage.USER_MESSAGE,
        text=data['text'],
        image=data['image']
    )
    ticket_message.save()

    if data['image'] is not None:
        os.remove(image_path)

    return ticket.id


def update_ticket(ticket_id: int, text: str):
    ticket = Ticket.objects.get(id=ticket_id)

    last_message = list(TicketMessage.objects.filter(ticket=ticket).order_by('id'))[-1]

    if last_message.message_type == TicketMessage.OPERATOR_MESSAGE:
        new_message = TicketMessage(
            ticket=ticket,
            message_type=TicketMessage.USER_MESSAGE,
            text=text
        )
        new_message.save()
    else:
        last_message.text = last_message.text + '\n\n' + text
        last_message.save()


def get_bots() -> list[Bot]:
    return Bot.objects.all()


def get_bot_by_token(token: str) -> Bot:
    return Bot.objects.get(token=token)


def update_bot_port(bot: Bot, port: int):
    bot.current_port = port
    bot.save()


def get_client_by_telegram(telegram_id: str) -> Client:
    return Client.objects.get(telegram_id=telegram_id)


def update_client_step(client: Client, course: Course, new_step: str):
    client.current_steps[course.id] = new_step
    client.save()


def get_test_by_id(test_id: int) -> Test:
    return Test.objects.get(id=test_id)


def get_survey_by_id(survey_id) -> Survey:
    return Survey.objects.get(id=survey_id)


def insert_user_answer(
        client: Client,
        survey: Survey,
        question: SurveyQuestion,
        answer: str
):
    answer = SurveyUserAnswer(
        user=client,
        survey=survey,
        question=question,
        answer=answer
    )
    answer.save()


def get_test_questions(test: Test) -> List[TestQuestion]:
    return list(TestQuestion.objects.filter(test=test))


def get_survey_questions(survey: Survey) -> List[SurveyQuestion]:
    return list(SurveyQuestion.objects.filter(survey=survey))


def get_closest_test_event(test: Test, threshold: int) -> TestEvent:
    events = list(TestEvent.objects.filter(test=test).order_by('threshold'))

    for event in events:
        if event.threshold >= threshold:
            return event

    return events[-1]


def get_trainers(event: TestEvent) -> List[Trainer]:
    trainers = []

    for training in event.training.all():
        trainers.append(training.trainer)

    return trainers


def get_training(trainer_name: str, event_id: str) -> Training:
    trainer = Trainer.objects.get(name=trainer_name)
    trainings = TestEvent.objects.get(id=event_id).training.all()

    for training in trainings:
        if training.trainer == trainer:
            return training


def get_default_training(test: Test) -> Optional[Training]:
    events = list(TestEvent.objects.filter(test=test).order_by('threshold'))

    print(events)

    for event in events:
        print(event)
        print(event.training.all())
        if event.training.all():
            return event.training.all()[0]

    return None


def add_course_passed(client: Client, course_id: int):
    course = Course.objects.get(id=course_id)

    client.courses_passed.add(course)
    client.current_courses.remove(course)
    client.save()


def get_client_course_by_bot(client: Client, bot: Bot) -> Optional[Course]:
    courses = client.current_courses.all()

    for course in courses:
        if course.bot == bot:
            return course

    return None
