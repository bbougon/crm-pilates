import logging

import sib_api_v3_sdk
from sib_api_v3_sdk import GetSmtpTemplates
from sib_api_v3_sdk.rest import ApiException

from crm_pilates.domain.email_notifier import MessageNotifier, Message
from crm_pilates.settings import config

logger = logging.getLogger("MessageNotifier")


class BrevoMessageNotifier(MessageNotifier):
    def __init__(self) -> None:
        super().__init__()
        self.configuration = sib_api_v3_sdk.Configuration()
        self.configuration.api_key["api-key"] = config("BREVO_API_KEY")

    def send(self, message: Message):

        try:
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
                sib_api_v3_sdk.ApiClient(self.configuration)
            )
            reponse: GetSmtpTemplates = api_instance.get_smtp_templates(
                limit=50, offset=0
            )
            template = list(
                filter(
                    lambda template: template.name == message["body"]["template"],
                    reponse.templates,
                )
            ).pop()
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": message["to"]}], template_id=template.id
            )
            api_instance.send_transac_email(send_smtp_email)
        except ApiException as e:
            logger.warning(
                "Something went wrong with Brevo API when sending an email:", e
            )
        except Exception as e:
            logger.warning("Something went wrong while sending the email:", e)
