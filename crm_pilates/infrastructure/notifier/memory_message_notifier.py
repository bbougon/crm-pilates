import logging

from crm_pilates.domain.email_notifier import MessageNotifier, Message

logger = logging.getLogger("MessageNotifier")


class MemoryMessageNotifier(MessageNotifier):
    def send(self, message: Message):
        logger.info("Sending message %s", message["body"]["template"])
