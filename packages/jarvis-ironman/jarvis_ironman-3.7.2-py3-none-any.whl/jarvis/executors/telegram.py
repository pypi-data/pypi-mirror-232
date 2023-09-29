import importlib
import logging
import os
import time

from jarvis.executors import controls
from jarvis.modules.exceptions import BotInUse, EgressErrors
from jarvis.modules.logger import logger, multiprocessing_logger
from jarvis.modules.models import models
from jarvis.modules.telegram.bot import TelegramBot

importlib.reload(module=logging)

FAILED_CONNECTIONS = {'count': 0}


def telegram_api() -> None:
    """Initiates polling for new messages.

    Handles:
        - BotInUse: Restarts polling to take control over.
        - ConnectionError: Initiates after 10, 20 or 30 seconds. Depends on retry count. Restarts after 3 attempts.
    """
    multiprocessing_logger(filename=os.path.join('logs', 'telegram_api_%d-%m-%Y.log'))
    if not models.env.bot_token:
        logger.info("Bot token is required to start the Telegram Bot")
        return
    try:
        TelegramBot().poll_for_messages()
    except BotInUse as error:
        logger.error(error)
        logger.info("Restarting message poll to take over..")
        telegram_api()
    except EgressErrors as error:
        logger.error(error)
        FAILED_CONNECTIONS['count'] += 1
        if FAILED_CONNECTIONS['count'] > 3:
            logger.critical("ATTENTION::Couldn't recover from connection error. Restarting current process.")
            controls.restart_control(quiet=True)
        else:
            logger.info("Restarting in %d seconds.", FAILED_CONNECTIONS['count'] * 10)
            time.sleep(FAILED_CONNECTIONS['count'] * 10)
            telegram_api()
    except Exception as error:
        logger.critical("ATTENTION: %s", error.__str__())
        controls.restart_control(quiet=True)
