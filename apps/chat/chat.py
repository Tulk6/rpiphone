import pyray as pr
import apps.chat.xmppManager as xmppManager
import tomllib, yaml

class ConversationObject:
    def __init__(self, jid, contact, mstr):
        self.mstr = mstr

        self.jid = jid
        self.contact = contact
        print(contact)

    def drawName(self, x, y):
        displayName = f'{self.contact["name"]} [{self.jid}]'
        if len(displayName) > 23:
            displayName = displayName[:19] + '...]'
        pr.draw_text_ex(self.mstr.terminalFont, displayName, (x+4, y+5), 16, 1, self.mstr.WHITE)
        pr.draw_text_ex(self.mstr.terminalFont, self.contact['status'], (x+4, y+23), 16, 1, self.mstr.WHITE)

    def drawOval(self, x, y):
        pr.draw_rectangle_rounded_lines(pr.Rectangle(x,y, 220, 40), 0.5, 2, 1, self.mstr.WHITE)

    def draw(self, x, y):
        self.drawOval(x, y)
        self.drawName(x, y)

class App:
    def __init__(self, mstr):
        self.mstr = mstr
        self.loadSettings()
        self.loadAddressBook() #address book is local to the phone !
                                #contacts is local to XMPP server

        self.xmppManager = xmppManager.XMPPManager(self.settings['xmpp']['username'],
                                                   self.settings['xmpp']['password'],
                                                   self.settings['xmpp']['server'])
        
        self.xmppManager.openClient()
        self.xmppManager.registerHandlers(self.handleMessage, self.handleMessage)
        self.xmppContacts = self.xmppManager.getContacts()

        self.loadConversations()

        self.state = 'Conversations' #app should start showing the lsit of contacts

        self.background = pr.load_texture('apps/chat/background5.png')

    def handleMessage(self, con, event):
        print(event.getType())
        print(event.getBody())

    def loadConversations(self):
        self.conversations = []
        for jid, contact in self.xmppContacts.items():
                self.conversations.append(ConversationObject(jid, contact, self.mstr))

    def loadSettings(self):
        with open('apps/chat/index.toml', 'rb') as file:
            self.settings = tomllib.load(file)['settings']
            print(self.settings)

    def loadAddressBook(self):
        with open('user/address_book/address_book.yaml', 'r') as file:
            self.addressBook = yaml.safe_load(file)

    def update(self):
        pass

    def draw(self):
        pr.draw_texture(self.background, 0, 0, pr.WHITE)
        if self.state == 'Conversations': #go through every contact 
            for i, conversation in enumerate(self.conversations):
                conversation.draw(10, 55+(i*50))

    def close(self):
        pr.unload_texture(self.background)
