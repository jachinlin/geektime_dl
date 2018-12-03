# coding=utf8

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib


class MailServer(object):
    """Represents an SMTP server, able to send outgoing emails, with SSL and TLS capabilities."""

    def __init__(self, host, port, user, password, encryption, timeout=60):
        self._smtp_host = host
        self._smtp_port = port
        self._smtp_user = user
        self._smtp_pass = password
        self._smtp_encryption = encryption
        self._smtp_timeout = timeout

    def test_smtp_connection(self):
        smtp = False
        try:
            smtp = self.connect()
        except Exception as e:
            raise Exception("Connection Test Failed! Here is what we got instead:\n %s" % e)
        finally:
            try:
                if smtp:
                    smtp.quit()
            except Exception:
                # ignored, just a consequence of the previous exception
                pass
        print("Connection Test Succeeded! Everything seems properly set up!")

    def connect(self):
        """Returns a new SMTP connection to the given SMTP server."""

        smtp_server = self._smtp_host
        smtp_port = self._smtp_port
        smtp_user = self._smtp_user
        smtp_password = self._smtp_pass
        smtp_encryption = self._smtp_encryption

        if smtp_encryption == 'ssl':
            connection = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=self._smtp_timeout)
        else:
            connection = smtplib.SMTP(smtp_server, smtp_port, timeout=self._smtp_timeout)
        if smtp_encryption == 'starttls':
            connection.starttls()

        connection.login(smtp_user, smtp_password)
        return connection

    def build_email(self, email_to, subject, body, attachments=None, subtype='plain'):
        """Constructs an RFC2822 email.message.Message object based on the keyword arguments passed, and returns it.

           :param list email_to: list of recipient addresses (to be joined with commas)
           :param string subject: email subject (no pre-encoding/quoting necessary)
           :param string body: email body, of the type ``subtype`` (by default, plaintext).
                               If html subtype is used, the message will be automatically converted
                               to plaintext and wrapped in multipart/alternative, unless an explicit
                               ``body_alternative`` version is passed.
           :param string subtype: optional mime subtype for the text body (usually 'plain' or 'html'),
                                  must match the format of the ``body`` parameter. Default is 'plain',
                                  making the content part of the mail "text/plain".
           :param list attachments: list of (filename, filecontents) pairs, where filecontents is a string
                                    containing the bytes of the attachment

           :return: the new RFC2822 email message
        """

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['To'] = email_to
        msg['Date'] = formatdate()

        email_text_part = MIMEText(body or u'', _subtype=subtype, _charset='utf-8')
        msg.attach(email_text_part)

        if attachments:
            for (fname, fcontent) in attachments:
                part = MIMEBase('application', "octet-stream")
                part.set_param('name', fname)
                part.add_header('Content-Disposition', 'attachment', filename=fname)
                part.set_payload(fcontent)
                encoders.encode_base64(part)
                msg.attach(part)
        return msg

    def send_email(self, message):
        """Sends an email"""

        try:
            smtp = self.connect()
            try:
                smtp.sendmail(self._smtp_user, message['To'], message.as_string())
            finally:
                smtp.quit()
        except Exception as e:

            raise Exception("Mail Delivery Failed:%s" % e)



