import xmpp, time

class XMPPManager:
    def __init__(self, username, password, server):
        self.username = username
        self.address = f'{username}@{server}'
        self.password = password
        self.server = server

        self.client = None

    def registerHandlers(self, presenceFunction, messageFunction):
        self.client.RegisterHandler('presence', presenceFunction)
        self.client.RegisterHandler('message', messageFunction)

    def sendMessage(self, msg, recipient):
        message = xmpp.Message(to=recipient, body=msg)
        self.client.send(message)

    def sendOnlinePresence(self, recipient, presence):
        pres = xmpp.Presence(to=recipient, status=presence)
        self.client.send(pres)

    def sendOfflinePresence(self, recipient):
        pres = xmpp.Presence(to=recipient, show='unavailable')
        self.client.send(pres)

    def process(self):
        self.client.Process()

    def getContacts(self):
        contactsDict = {}
        print(self.address)
        for jid in self.contacts.getItems():
            if jid != self.address:
                print(jid)
                print(self.contacts.getStatus(jid))
                contactsDict[jid] = {'name': self.contacts.getName(jid),
                                        'status': self.contacts.getStatus(jid),
                                        'show': self.contacts.getShow(jid)}

        return contactsDict

    def deleteContact(self, jid):
        self.contacts.delItem(jid)

    def addContact(self, jid):
        self.contacts.setItem(jid)

    def openClient(self):
        self.client = xmpp.Client(self.server)
        self.client.connect()
        self.client.auth(self.username, self.password)
        self.client.sendInitPresence()
        self.contacts = self.client.getRoster()

    def closeClient(self):
        self.client.disconnect()
