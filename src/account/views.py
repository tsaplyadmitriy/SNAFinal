import json
import logging
import os

import requests
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .database import get_bot_by_token

logger = logging.getLogger(__name__)
logging.getLogger('urllib').setLevel(logging.WARNING)


@csrf_exempt
def get_updates(request, token):
    os.environ['no_proxy'] = '127.0.0.1,localhost'
    if request.method == 'POST':
        port = get_bot_by_token(token).current_port
        data = json.loads(request.body)
        headers = request.headers

        logger.debug(f'{port} - {data}')

        r = requests.post(
            'http://tgbot:' + str(port) + '/bot/' + token,
            json=data,
            headers=headers
        )

        return HttpResponse('Success')
