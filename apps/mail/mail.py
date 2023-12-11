import pyray as pr
import apps.mail.emailManager as emailManager
import tomllib, datetime, threading, re, textwrap, math
import markdownify as mdfy
import menuUtils as mu

#imap.store being really dumb and annoyign

# THREADING IS FUCKING WITH IMAP RESPONSES HENCE UNEXPECTED RESPONSE !!!!

class InboxItem:
    textwrapper = textwrap.TextWrapper(replace_whitespace=False, width=28)

    def __init__(self, emailObject, master):
        self.emailObject = emailObject
        self.mstr = master

        self.shortSubject = self.emailObject.subject
        self.shortBody = self.emailObject.body
        self.shortSender = self.emailObject.senderName
        
        wrappedLines = []
        for line in self.emailObject.body.splitlines():
            wrappedLines.append('\n'.join(InboxItem.textwrapper.wrap(line)))

        self.body = '\n'.join(wrappedLines)
        #print(self.body)

        if len(self.emailObject.subject) > 30:
            self.shortSubject = self.shortSubject[:27]+'...'
        if len(self.shortBody) > 30:
            self.shortBody = self.shortBody.replace('\n', ' ')[:27]+'...'
        if len(self.shortSender) > 22:
            self.shortSender = self.shortSender[:19]+'...'

    def draw(self, pos, focus=False):
        if focus:
            blue = self.mstr.mstr.LIGHT_BLUE
            white = self.mstr.mstr.WHITE
            height = 60
        else:
            blue = self.mstr.mstr.HALF_BLUE
            white = self.mstr.mstr.HALF_WHITE
            height = 45
        pr.draw_rectangle_rounded(pr.Rectangle(pos[0]+5, pos[1], 230, height), 0.5, 3, blue)

        pr.draw_text_ex(self.mstr.mstr.uiFont, 'From: ', (pos[0]+13, pos[1]+5), 16, 1, self.mstr.mstr.GREEN)
        pr.draw_text_ex(self.mstr.mstr.uiFont, self.shortSender, (pos[0]+60, pos[1]+5), 16, 1, white)

        pr.draw_text_ex(self.mstr.mstr.uiFont, self.shortSubject, (pos[0]+13, pos[1]+20), 16, 1, white)

        if focus:
            pr.draw_text_ex(self.mstr.mstr.uiFont, self.shortBody, (pos[0]+13, pos[1]+35), 16, 1, white)

class App:
    def __init__(self, master):
        self.mstr = master
        mu.associateMaster(master)

        self.loadSettings()

        self.mailbox = emailManager.EmailManager(self.settings['email']['address'],self.settings['email']['imap'],
                                                 self.settings['email']['smtp'],self.settings['email']['password'])
        #self.mailbox.loadInbox()

        self.emailCount = None
        self.emailThread = threading.Thread(target=self.getAllEmails) #threading email collection so draw still runs
        self.emailThread.start()

        self.wallpaper = pr.load_texture('apps/mail/follow.png')
        
        self.selectedEmail = None
        self.emailIndexInPage = 0

        self.currentScreen = 'inbox'
        self.stage = None
        self.menu = False
        self.currentLine = 0
        self.emailsPerPage = 5
        self.currentPageIndex = 0
        self.numberOfPages = 0

        self.textWrapper = textwrap.TextWrapper(replace_whitespace=False, width=28)

        self.textLogger = mu.TextLogger()

        self.inboxMenu = mu.PopUpMenu({'New Email':self.beginDrafting, 'Reload Inbox':''})
        self.subjectEntry = mu.TextEntryDialogue('Enter Subject')
        self.addressEntry = mu.TextEntryDialogue('Enter Recipient')
        self.yesNoSend = mu.YesNoDialogue('Send Email?')

    def getAllEmails(self):
        self.mailbox.loadInbox()
        numberOfEmails = self.mailbox.fetchEmails(numberOfEmails=0)[1]
        self.inbox = []
        blockSize = 10
        numberOfBlocks = math.floor(numberOfEmails/blockSize)
        additionalBlockSize = numberOfEmails % blockSize
        self.selectedEmail = 0
        self.emailCount = self.mailbox.fetchEmails(numberOfEmails=0)[1]
        self.numberOfPages = math.ceil(self.emailCount/self.emailsPerPage)
        i = -1
        for i in range(numberOfBlocks):
            self.inbox += [InboxItem(i, self) for i in self.mailbox.fetchEmails(startIndex=i*blockSize, numberOfEmails=blockSize)[0]]
        print('done loop')
        self.inbox += [InboxItem(i, self) for i in self.mailbox.fetchEmails(startIndex=(i+1)*blockSize, numberOfEmails=additionalBlockSize)[0]]
        #self.emailCount = self.mailbox.fetchEmails(numberOfEmails=0)[1]

    def getEmails(self, startIndex=0, numberOfEmails=10):
        self.inbox = []
        emailFetch = self.mailbox.fetchEmails(startIndex=startIndex, numberOfEmails=numberOfEmails)
        self.emailCount = emailFetch[1]
        self.numberOfPages = math.ceil(self.emailCount/self.emailsPerPage)
        for email in emailFetch[0]:
            self.inbox.append(InboxItem(email, self))
        self.selectedEmail = 0

    def loadSettings(self):
        with open('apps/mail/index.toml', 'rb') as file:
            self.settings = tomllib.load(file)['settings']

    def setEmailIndex(self, index):
        self.selectedEmail = min(max(0, index), self.emailCount-1)
        self.currentPageIndex = math.floor(self.selectedEmail/self.emailsPerPage)
        self.emailIndexInPage = self.selectedEmail % self.emailsPerPage

    def setPageNumber(self, index):
        self.numberOfPages = math.ceil(self.emailCount/self.emailsPerPage)
        if 0<=index<self.numberOfPages:
            self.currentPageIndex = index
            self.emailIndexInPage = 0
            self.selectedEmail = index*self.emailsPerPage

    def setEmailIndexInPage(self, index):
        self.selectedEmail = (self.currentPageIndex*self.emailsPerPage)+(index % self.emailsPerPage)
        if index > self.emailsPerPage:
            self.setPageNumber(self.currentPageIndex+1)
        else:
            self.emailIndexInPage = index % self.emailsPerPage
        
    def beginDrafting(self):
        self.currentScreen = 'drafting'
        self.menu = False
        self.subjectEntry.focus()
        self.stage = 'subject'

    def buildAndSendEmail(self):
        builtEmail = emailManager.EmailObject(recipient=self.draftAddress,
                                              subject=self.draftSubject,
                                              body=self.draftBody)
        self.mailbox.sendEmail(builtEmail)
        print('sent!')

    def draw(self):
        pr.draw_texture(self.wallpaper, 0, 0, self.mstr.WHITE)
        pr.draw_rectangle_gradient_v(0, 0, 240, 23, self.mstr.LIGHT_BLUE, self.mstr.DARK_BLUE)
        pr.draw_rectangle_gradient_v(0, 23, 240, 2, self.mstr.DARK_BLUE, self.mstr.BLACK)
        if self.currentScreen == 'inbox':
            if self.emailCount is None: #if emails have not been loaded yet, show loading emails
                numberOfDots = (int(pr.get_time()) % 3) + 1 #add a dot each second until 3, then back to one
                pr.draw_text_ex(self.mstr.headingFont, f'Loading your emails{numberOfDots*"."}', (10, 2), 20, 1, self.mstr.WHITE)
            else:
                pr.draw_text_ex(self.mstr.headingFont, f'You have {self.emailCount} emails', (10, 2), 20, 1, self.mstr.WHITE)

            pr.draw_rectangle(100, 300, 40, 20, self.mstr.DARK_BLUE)
            pageIndexStringWidth = pr.measure_text_ex(self.mstr.uiFont, f'{self.currentPageIndex+1}/{self.numberOfPages}', 16, 1).x
            pageStringOffset = (40 - pageIndexStringWidth)/2
            pr.draw_text_ex(self.mstr.uiFont, f'{self.currentPageIndex+1}/{self.numberOfPages}', (100+pageStringOffset, 300), 16, 1, self.mstr.WHITE)

            if self.selectedEmail is not None and self.emailCount is not None: #email count is known as emails have been loaded
                firstEmailInPage = self.currentPageIndex*self.emailsPerPage
                lastEmailInPage = min(self.emailCount, firstEmailInPage + self.emailsPerPage)
                for email, i in zip(self.inbox[firstEmailInPage:lastEmailInPage], range(firstEmailInPage, lastEmailInPage)):
                    indexInPage = i - (self.currentPageIndex*self.emailsPerPage)
                    if i < self.selectedEmail: #email is drawn above expanded selected email, so higher up
                        email.draw((0, indexInPage*50+30))
                    elif i == self.selectedEmail: #email is expanded, focus is true
                        email.draw((0, indexInPage*50+30), focus=True)
                    else: #email is drawn below expanded email, so lower down
                        email.draw((0, indexInPage*50+45))

                if self.menu:
                    self.inboxMenu.drawMenu()

        elif self.currentScreen == 'email': #current screen is displaying an email
            bodyText = '\n'.join(self.inbox[self.selectedEmail].body.splitlines()[self.currentLine:]) #allows scrolling through text 
            pr.draw_rectangle(0, 25, 240, 320, self.mstr.MORE_BLUE) #dim background
            pr.draw_text_ex(self.mstr.headingFont, self.inbox[self.selectedEmail].shortSubject, (10, 2), 20, 1, self.mstr.WHITE)
            pr.draw_text_ex(self.mstr.monoFont, bodyText, (7, 32), 14, 1, self.mstr.BLACK)
            pr.draw_text_ex(self.mstr.monoFont, bodyText, (5, 30), 14, 1, self.mstr.WHITE)

            if pr.is_key_pressed(pr.KEY_BACKSPACE):
                self.currentScreen = 'inbox'
            
            if pr.is_key_pressed(pr.KEY_UP) and bodyText != '':
                self.currentLine = (self.currentLine - 1) % len(self.inbox[self.selectedEmail].body.splitlines())
            elif pr.is_key_pressed(pr.KEY_DOWN) and bodyText != '':
                self.currentLine = (self.currentLine + 1) % len(self.inbox[self.selectedEmail].body.splitlines())

            if pr.is_key_pressed(pr.KEY_LEFT):
                self.selectedEmail = (self.selectedEmail - 1) % self.emailsPerPage
                self.currentLine = 0
            elif pr.is_key_pressed(pr.KEY_RIGHT):
                self.selectedEmail = (self.selectedEmail + 1) % self.emailsPerPage
                self.currentLine = 0
            
            if pr.is_key_pressed(pr.KEY_D):
                response, message_data = self.mailbox.imap.search(None, 'ALL')
                seq = message_data[0].split()[0]
                print(seq)
                self.mailbox.deleteEmail(seq)

        elif self.currentScreen == 'drafting':
            if self.stage == 'subject':
                self.subjectEntry.draw()
            elif self.stage == 'address':
                self.addressEntry.draw()
            elif self.stage == 'body':
                body = '\n'.join(self.textWrapper.wrap(self.textLogger.returnText()))
                pr.draw_text_ex(self.mstr.headingFont, self.draftSubject, (10, 2), 20, 1, self.mstr.WHITE)
                pr.draw_text_ex(self.mstr.monoFont, body, (7, 32), 14, 1, self.mstr.BLACK)
                pr.draw_text_ex(self.mstr.monoFont, body, (5, 30), 14, 1, self.mstr.WHITE)

            if self.stage == 'ask':
                self.yesNoSend.draw()
            elif pr.is_key_pressed(pr.KEY_BACKSPACE):
                self.currentScreen = 'inbox'
                self.subjectEntry.unfocus()
                self.addressEntry.unfocus()
                self.textLogger.stop()

    def update(self):
        if pr.is_key_pressed(pr.KEY_RIGHT_SHIFT)  or (self.menu and pr.is_key_pressed(pr.KEY_BACKSPACE)):
            self.menu = not self.menu

        if self.currentScreen == 'inbox':
            if self.menu: #the menu is currently up
                self.inboxMenu.update()
            else:
                if pr.is_key_pressed(pr.KEY_UP):
                    self.setEmailIndex(self.selectedEmail-1)
                    #print(self.selectedEmail)
                elif pr.is_key_pressed(pr.KEY_DOWN):
                    self.setEmailIndex(self.selectedEmail+1)
                    #print(self.selectedEmail)

                if pr.is_key_pressed(pr.KEY_RIGHT):
                    self.setPageNumber(self.currentPageIndex+1)
                if pr.is_key_pressed(pr.KEY_LEFT):
                    self.setPageNumber(self.currentPageIndex-1)
        
                if pr.is_key_pressed(pr.KEY_ENTER):
                    #print(self.inbox[self.selectedEmail].emailObject.body)
                    self.currentScreen = 'email'
                    self.currentLine = 0
        elif self.currentScreen == 'drafting':
            if self.stage == 'subject':
                self.subjectEntry.update()
                if self.subjectEntry.getResponse() is not None:
                    self.draftSubject = self.subjectEntry.getResponse()
                    self.subjectEntry.unfocus()
                    self.addressEntry.focus()
                    self.stage = 'address'
            elif self.stage == 'address':
                self.addressEntry.update()
                if self.addressEntry.getResponse() is not None:
                    self.draftAddress = self.addressEntry.getResponse()
                    self.addressEntry.unfocus()
                    self.stage = 'body'
                    self.textLogger.start()
            elif self.stage == 'body':
                self.textLogger.update()
                if pr.is_key_pressed(pr.KEY_ENTER):
                    self.stage = 'ask'
                    self.draftBody = self.textLogger.returnText()
                    self.textLogger.stop()
            elif self.stage == 'ask':
                self.yesNoSend.update()
                if self.yesNoSend.getResponse() is not None:
                    if self.yesNoSend.getResponse():
                        self.buildAndSendEmail()
                        self.currentScreen = 'inbox'
                    else:
                        self.stage = 'body'
                        self.textLogger.start()


    def close(self):
        self.mailbox.closeInbox()
        #kill thread??
        pr.unload_texture(self.wallpaper)
