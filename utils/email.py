import itertools
import logging
import time
from threading import Thread

from django.core.mail import EmailMessage, get_connection

MAX_ATTEMPTS = 5
BACKOFF_START = 1
BACKOFF_FACTOR = 2

logger = logging.getLogger(__name__)


def handle_mail_error(
    error: Exception,
    emails_not_sent: list[EmailMessage],
    emails_sent: list[EmailMessage],
    to: list[str] | None = None,
) -> None:
    """Callback called when an error occures while sending batched emails."""

    dotkom_address = "dotkom@online.ntnu.no"
    bcc = None
    if to is not None and dotkom_address not in to:
        bcc = [dotkom_address]

    not_sent_recipients = list(
        itertools.chain.from_iterable(em.recipients() for em in emails_not_sent)
    )
    sent_recipients = list(
        itertools.chain.from_iterable(em.recipients() for em in emails_sent)
    )

    message = (
        f"An error occured while attempting to send batch emails.\n"
        f"This message is automatically forwarded to Dotkom, but your group receives this as well for verbose purposes.\n\n"
        f"The email:\n"
        f"---------------------------------------------------------------------------\n"
        f"{emails_not_sent[0].message()}\n"
        f"---------------------------------------------------------------------------\n\n"
        f"Error message: {error}\n"
        f"Total of addresses that successfully received the email: {len(sent_recipients)}\n"
        f"Total of addresses that did not receive the email: {len(not_sent_recipients)}\n"
        f"Addresses that successfully received the email: {', '.join(sent_recipients) if sent_recipients else 'None'}\n"
        f"Addresses that did not receive the email: {', '.join(not_sent_recipients) if not_sent_recipients else 'None'}\n"
    )

    # Sending a regular EmailMessage because if anything other breaks, we are doomed either way.
    email = EmailMessage(
        subject="An error occured while sending emails",
        body=message,
        from_email="onlineweb4-error@online.ntnu.no",  # TODO: Change??
        to=to or [],
        bcc=bcc,
    )
    email.send()

    logger.info(f"Sent error email to {', '.join((to or []) + (bcc or []))}")


class AutoChunkedEmailMessage:
    def __init__(
        self,
        subject="",
        body="",
        from_email=None,
        to=None,
        bcc=None,
        connection=None,
        attachments=None,
        headers=None,
        cc=None,
        reply_to=None,
    ):
        self.kwargs = {
            "subject": subject,
            "body": body,
            "from_email": from_email,
            "to": to,
            "bcc": bcc,
            "connection": connection,
            "attachments": attachments,
            "headers": headers,
            "cc": cc,
            "reply_to": reply_to,
        }

    def _create_chunks(self):
        to = self.kwargs.get("to") or []
        cc = self.kwargs.get("cc") or []
        bcc = self.kwargs.get("bcc") or []

        def create_chunk():
            return {
                "to": [],
                "cc": [],
                "bcc": [],
            }

        chunks = []
        chunk = create_chunk()

        def set_in_chunk(key, value):
            nonlocal chunk

            if sum(len(v) for v in chunk.values()) >= 50:
                chunks.append(chunk)
                chunk = create_chunk()

            chunk[key].append(value)

        for x in to:
            set_in_chunk("to", x)

        for x in cc:
            set_in_chunk("cc", x)

        for x in bcc:
            set_in_chunk("bcc", x)

        if sum(len(v) for v in chunk.values()) > 0:
            chunks.append(chunk)

        return chunks

    def _send(self, emails, error_callback=None, fail_silently=False):  # noqa: C901
        not_sent = emails.copy()

        tries = 0
        backoff = BACKOFF_START
        while True:
            tries += 1

            successes = []

            for email in not_sent:
                try:
                    email.send(fail_silently=fail_silently)
                except Exception as e:

                    def rethrow(not_sent=not_sent, e=e):
                        try:
                            if callable(error_callback):
                                error_callback(
                                    e,
                                    not_sent,  # Email objects not sent
                                    [
                                        em for em in emails if em not in not_sent
                                    ],  # Email objects that has been sent
                                )
                        finally:
                            raise

                    # This is ultimately the weird bug that this whole class is trying to fix.
                    if "Recipient count exceeds 50" in str(e):
                        logger.debug("Recipient count exceeds 50?, retrying soon.")
                    else:
                        rethrow()

                    if tries >= MAX_ATTEMPTS:
                        rethrow()
                else:
                    successes.append(email)

            if len(successes) == len(not_sent):
                break

            not_sent = [x for x in not_sent if x not in successes]

            backoff *= BACKOFF_FACTOR
            logger.debug(
                f"Failed to send {len(not_sent)} emails, retrying in {backoff} seconds"
            )
            time.sleep(backoff)

    def send(self, error_callback=None, fail_silently=False):
        # Use a shared connection in order for throttling to be properly handled using django-ses.
        # https://github.com/django-ses/django-ses/blob/f9ebfab30d2b8dab9a9c73fc9ec2f36037533e65/django_ses/__init__.py#L154
        connection = get_connection()
        logger.info("Using connection type %s to send emails", type(connection))
        self.kwargs["connection"] = connection

        chunks = self._create_chunks()

        emails = [
            EmailMessage(
                **self.kwargs | chunk,
            )
            for chunk in chunks
        ]

        self._send(
            emails,
            error_callback=error_callback,
            fail_silently=fail_silently,
        )

    def send_in_background(self, error_callback=None, fail_silently=False):
        """Same as send() but utilizes a thread to send the emails in the background."""
        thread = Thread(
            target=self.send,
            kwargs={
                "error_callback": error_callback,
                "fail_silently": fail_silently,
            },
        )
        thread.start()

        return thread
