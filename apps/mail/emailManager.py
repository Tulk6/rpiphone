import smtplib, email, imaplib, email.policy, datetime, email.mime.text

#TODO:
# - rewrite email collection so that emails can be formed just from to + from + subject, 
#   instead of loading whole RFC822, use UID BODY[TEXT]

monthNumbers = {'Jan': 1,
                'Feb': 2,
                'Mar': 3,
                'Apr': 4,
                'May': 5,
                'Jun': 6,
                'Jul': 7,
                'Aug': 8,
                'Sep': 9,
                'Oct': 10,
                'Nov': 11,
                'Dec': 12}

class EmailObject:
    def __init__(self, sender=None, recipient=None, subject=None, body=None, date=None):
        if sender is not None:
            senderAddress = sender.addresses[0]
            self.sender = senderAddress.username+'@'+senderAddress.domain
            self.senderName = senderAddress.display_name
        self.recipient = recipient
        self.subject = subject
        self.body = body
        #print(body)
        self.date = date

    def findBodyText(self, message):
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True) #to control automatic email-style MIME decoding (e.g., Base64, uuencode, quoted-printable)
                    body = body.decode()

    def fromBytes(byt):
        message = email.message_from_bytes(byt, policy=email.policy.default)
        
        body = ''
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True) #to control automatic email-style MIME decoding (e.g., Base64, uuencode, quoted-printable)
                    try:
                        body = body.decode()
                    except UnicodeDecodeError as e:
                        body = '__ERROR__\nTHERE WAS AN ERROR ATTEMPTING TO DECODE THIS EMAIL\nERROR IS AS FOLLOWS:\n'+str(e)

        date = message['date'].split(', ')[1].split(' ')
        time = list(map(int, message['date'].split(', ')[1].split(' ')[3].split(':')))
        hoursOffset = int(date[4][0:3])
        minutesOffset = int(date[4][3:])
        date = datetime.datetime(int(date[2]), monthNumbers[date[1]], int(date[0]), time[0], time[1],
                                 tzinfo=datetime.timezone(datetime.timedelta(hours=hoursOffset,
                                                                             minutes=minutesOffset)))
        
        return EmailObject(sender=message['from'], recipient=str(message['to']), subject=str(message['subject']),
                           body=body, date=date)
    

class EmailManager:
    def __init__(self, address, imapServer, smtpServer, password, timezone=datetime.timezone.utc):
        self.address = address
        self.imapServer = imapServer
        self.smtpServer = imapServer
        self.password = password

        self.timezone = timezone

    def loadInbox(self):
        self.imap = imaplib.IMAP4_SSL(self.imapServer)
        self.imap.login(self.address, self.password)
    
    def closeInbox(self):
        self.imap.close()
        self.imap.logout()

    def deleteEmail(self, index):
        #typ, data = self.imap.search(None, 'ALL')
        #print(data)
        try:
            self.imap.store(index, '+FLAGS', '(\HELLO)')
        except imaplib.IMAP4.abort as e:
            print(e)

    def fetchEmails(self, startIndex=0, numberOfEmails=10):
        status, emailNumber = self.imap.select('inbox') #opening inbox
        emailNumber = int(emailNumber[0])
        latestEmail = emailNumber

        emails = []
        for i in range(0, numberOfEmails):
            status, emailResponse = self.imap.fetch(str(latestEmail-startIndex-i), '(RFC822)')
            emails.append(EmailObject.fromBytes(emailResponse[0][1]))

        return emails, emailNumber

    def sendEmail(self, emailObject):
        message = email.mime.text.MIMEText(emailObject.body, 'html')
        message['from'] = self.address
        message['to'] = emailObject.recipient
        message['subject'] = emailObject.subject

        smtp = smtplib.SMTP_SSL(self.smtpServer)
        smtp.login(self.address, self.password)
        
        try:
            smtp.sendmail(self.address, emailObject.recipient, message.as_string())
            smtp.quit()
            return True
        except smtplib.SMTPRecipientsRefused:
            return False
