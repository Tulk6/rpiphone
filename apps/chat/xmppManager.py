import xmpp, time

class XMPPManager:
    def __init__(self, username, password, server):
        self.username = username
        self.address = f'{username}@{server}'
        self.password = password
        self.server = server

        self.client = None
        self.contacts = {}
        self.contactJids = []

    def updateContacts(self):
        self.contactJids = [jid for jid in self.roster.getItems() if jid != self.address]
        for jid in self.contactJids:
            self.contacts[jid] = {'name': self.roster.getName(jid),
                                  'status': self.roster.getStatus(jid),
                                  'show': self.roster.getShow(jid)}
        print(self.contacts)
    
    def chainedRosterUpdate(self, func):
        self.updateContacts()
        func()

    def registerHandlers(self, presenceFunction, messageFunction):
        self.client.RegisterHandler('presence', presenceFunction)
        self.client.RegisterHandler('message', messageFunction)

    def sendMessage(self, msg, recipient):
        message = xmpp.Message(to=recipient, body=msg)
        self.client.send(message)

    def sendPresenceToAll(self, status, show=None):
        for jid in self.contactJids:
            print(jid)
            self.sendOnlinePresence(jid, status, show=show)

    def sendOnlinePresence(self, recipient, presence, show=None):
        pres = xmpp.Presence(to=recipient, status=presence, show=show)
        self.client.send(pres)

    def sendUnavailablePresence(self, recipient):
        pres = xmpp.Presence(to=recipient, show='xa')
        self.client.send(pres)

    def process(self):
        self.client.Process()

    def deleteContact(self, jid):
        self.contacts.delItem(jid)

    def addContact(self, jid):
        self.contacts.setItem(jid)

    def openClient(self):
        self.client = xmpp.Client(self.server)
        self.client.connect()
        self.client.auth(self.username, self.password)
        self.client.sendInitPresence()
        self.roster = self.client.getRoster()
        self.updateContacts()

    def closeClient(self):
        self.client.disconnect()
