import pyray as pr
import apps.chat.xmppManager as xmppManager
import menuUtils as mu
import tomllib, yaml

class ConversationObject:
    def __init__(self, jid, contact, mstr):
        self.mstr = mstr

        self.jid = jid
        self.contact = contact

    def drawName(self, x, y):
        displayName = f'{self.contact["name"]} [{self.jid}]'
        if len(displayName) > 23:
            displayName = displayName[:19] + '...]'
        pr.draw_text_ex(self.mstr.terminalFont, displayName, (x+4, y+5), 16, 1, self.mstr.WHITE)
        pr.draw_text_ex(self.mstr.terminalFont, self.contact['status'], (x+4, y+23), 16, 1, self.mstr.WHITE)

    def drawOval(self, x, y):
        pr.draw_rectangle_rounded_lines(pr.Rectangle(x,y, 220, 40), 0.4, 2, 1, self.mstr.WHITE)

    def draw(self, x, y):
        self.drawOval(x, y)
        self.drawName(x, y)

class App:
    def __init__(self, mstr):
        self.mstr = mstr
        mu.associateMaster(mstr)
        self.loadSettings()
        self.loadAddressBook() #address book is local to the phone !
                                #contacts is local to XMPP server

        self.xmppManager = xmppManager.XMPPManager(self.settings['xmpp']['username'],
                                                   self.settings['xmpp']['password'],
                                                   self.settings['xmpp']['server'])
        
        self.xmppManager.openClient()
        self.xmppManager.sendUnavailablePresence('jamestulk@jabbers.one')#, 'Hello!', show='dnd')
        self.xmppManager.registerHandlers(self.handlePresence, self.handleMessage)

        self.state = 'Conversations' #app should start showing the lsit of contacts
        self.conversationIndex = 0

        self.chatMessages = []
        
        self.chatJid, self.chatContact = None, None

        self.showNames = {None: 'online :D',
                          'xa': 'out D:',
                          'dnd': 'busy :|',
                          'away': 'away :('}

        self.background = pr.load_texture('apps/chat/background.png')
        self.pixelFontHeading = pr.load_font_ex('ui/fonts/invasion2000.regular.ttf', 24, None, 0)

        self.textLogger = mu.TextLogger()
        self.textLogger.setKeyboard(False)

    def handlePresence(self, con, event):
        self.xmppManager.updateContacts()
        if self.chatJid is not None:
            self.chatContact = self.xmppManager.contacts[self.chatJid]
        #print(event.getType())
        #print(event.getBody())
        
    def handleMessage(self, con, event):
        #print('con' + str(type(con)))
        #print('event' + str(type(event)))
        #print(event.getType())
        #print('DATA HELLO is antQ!@ELOORLKRWLKJELJ')
        #print(event.getData())
        if event.getType() == 'chat' and event.getBody() is not None:
            #get from returns wack address with resouce, get stripped is usual node@domain.com
            self.chatMessages.append((self.xmppManager.roster.getName(event.getFrom().getStripped()), event.getBody()))
        elif event.getType() == 'error':
            print('---> ERROR: ', event.getBody())

    def determineDisplayShow(self, contact):
        if contact['status'] is None and contact['show'] is None: #an offline presence is None status and Show (available is None show)
            show = 'offline ._.'
        else:
            show = self.showNames[contact['show']] #apart from offline/available every other show is unique, so a display string is got from a dictionary

        return show
    
    def drawConversation(self, x, y, jid):
        contact = self.xmppManager.contacts[jid]

        show = self.determineDisplayShow(contact)
        status = contact['status'] if contact['status'] is not None else ''

        pr.draw_rectangle_rounded_lines(pr.Rectangle(x,y, 220, 40), 0.4, 2, 1, self.mstr.WHITE)

        #displayName = f'{contact["name"]} [{jid}]'
        #if len(displayName) > 23:
            #displayName = displayName[:19] + '...]'
        pr.draw_text_ex(self.mstr.uiFont, f'{contact["name"]} is {show}', (x+4, y+5), 16, 1, self.mstr.WHITE)

        pr.draw_text_ex(self.mstr.uiFont, f"Says '{status}'", (x+4, y+23), 16, 1, self.mstr.WHITE)

    def loadSettings(self):
        with open('apps/chat/index.toml', 'rb') as file:
            self.settings = tomllib.load(file)['settings']

    def loadAddressBook(self):
        with open('user/address_book/address_book.yaml', 'r') as file:
            self.addressBook = yaml.safe_load(file)

    def startChat(self, jid):
        self.state = 'Chat'
        self.chatJid = jid
        self.chatContact = self.xmppManager.contacts[jid]
        self.chatMessages = []
        self.textLogger.start()

    def sendMessageInCurrentChat(self, msg):
        self.chatMessages.append((self.xmppManager.username, msg))
        self.xmppManager.sendMessage(msg, self.chatJid)

    def update(self):
        self.xmppManager.process()
        if self.state == 'Conversations':
            if pr.is_key_pressed(pr.KEY_DOWN):
                self.conversationIndex = (self.conversationIndex+1)%len(self.xmppManager.contacts.keys())
            elif pr.is_key_pressed(pr.KEY_UP):
                self.conversationIndex = (self.conversationIndex-1)%len(self.xmppManager.contacts.keys())

            if pr.is_key_pressed(pr.KEY_ENTER):
                self.startChat(self.xmppManager.contactJids[self.conversationIndex])

        elif self.state == 'Chat':
            if pr.is_key_pressed(pr.KEY_ENTER):
                self.sendMessageInCurrentChat(self.textLogger.text)
                self.textLogger.reset()

        #print(self.xmppManager.contacts.getStatus('jamestulk@jabbers.one'))

    def draw(self):
        pr.draw_texture(self.background, 0, 0, pr.WHITE)
        if self.state == 'Conversations': #go through every contact 
            pr.draw_line_ex((10, 40), (240, 40), 4.0, self.mstr.WHITE)
            pr.draw_text_ex(self.pixelFontHeading, 'Conversations', (10, 8), 24, 1, self.mstr.WHITE)
            pr.draw_text_ex(self.mstr.uiFont, '>', (0, 65+(self.conversationIndex*50)), 16, 1, self.mstr.WHITE)
            for i, jid in enumerate(self.xmppManager.contacts.keys()):
                self.drawConversation(10, 55+(i*50), jid)
        elif self.state == 'Chat':
            pr.draw_line_ex((10, 40), (240, 40), 4.0, self.mstr.WHITE)
            pr.draw_text_ex(self.pixelFontHeading, self.chatContact['name'], (10, 8), 24, 1, self.mstr.WHITE)
            pr.draw_text_ex(self.mstr.uiFont, f'Currently {self.determineDisplayShow(self.chatContact)}',
                            (10, 46), 16, 1, self.mstr.WHITE)
            
            pr.draw_rectangle_rounded_lines(pr.Rectangle(10,270, 220, 40), 0.4, 2, 1, self.mstr.WHITE)
            pr.draw_text_ex(self.mstr.uiFont, self.textLogger.getText(), (10, 270), 16, 1, self.mstr.WHITE)

            for i, (sender, body) in enumerate(reversed(self.chatMessages)):
                pr.draw_text_ex(self.mstr.uiFont, f'{sender}: {body}', (10, 250-(12*i)), 16, 1, self.mstr.WHITE)


    def close(self):
        pr.unload_texture(self.background)

        self.xmppManager.closeClient()
