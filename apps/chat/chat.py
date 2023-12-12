import pyray as pr
import apps.chat.xmppManager as xmppManager
import tomllib, yaml

class App:
    def __init__(self, mstr):
        self.mstr = mstr
        self.loadSettings()
        self.loadAddressBook()

        self.xmppManager = xmppManager.XMPPManager(self.settings['xmpp']['username'],
                                                   self.settings['xmpp']['password'],
                                                   self.settings['xmpp']['server'])
        
        self.xmppManager.openClient()
        self.xmppContacts = self.xmppManager.getContacts()
        
        self.state = 'Contacts'

    def handleMessage(self, con, event):
        print(event.getType())
        print(event.getBody())

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
        if self.state == 'Contacts':
            for i, (jid, contact) in enumerate(self.xmppContacts.items()):
                pr.draw_text(f'{contact["name"]} {jid}', 0, i*20, 14, pr.WHITE)

    def close(self):
        pass
