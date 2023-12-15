import xmpp, time, omemo

class XMPPManager:
    NODE = 'JTPyXMPP'
    VERSION = '0.1'

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

    def registerHandlers(self, presenceFunction, messageFunction):
        self.client.RegisterHandler('presence', presenceFunction)
        self.client.RegisterHandler('message', messageFunction)

    def sendActiveInChatMarker(self, recipient):
        message = xmpp.Message(to=recipient, typ='chat')
        message.addChild(name='active', namespace='http://jabber.org/protocol/chatstates')
        self.client.send(message)

    def sendInactiveInChatMarker(self, recipient):
        message = xmpp.Message(to=recipient, typ='chat')
        message.addChild(name='inactive', namespace='http://jabber.org/protocol/chatstates')
        self.client.send(message)

    def handleCapIQ(self, conn, event):
        self.sendCapacities(event.getFrom(), event.getID())
        #here we raise an exception to stop the default handler from processing the iq
        raise xmpp.NodeProcessed
    
    def queryCapacities(self, recipient):
        iq = xmpp.Iq(to=recipient, typ='get')
        iq.addChild(name='query', namespace='http://jabber.org/protocol/disco#info')
        self.client.send(iq)

    def sendCapacities(self, recipient, id):
        query = xmpp.Node(tag='query', attrs={'xmlns': 'http://jabber.org/protocol/disco#info'})
        query.addChild(name='identity', attrs={'category': 'account', 'type': 'registered'})

        #all supported feature namespaces
        query.addChild(name='feature', attrs={'var': 'urn:xmpp:attention:0'}) #attention buzzes
        query.addChild(name='feature', attrs={'var': 'http://jabber.org/protocol/mood'})
        query.addChild(name='feature', attrs={'var': 'http://jabber.org/protocol/nick'}) #nicknames!
        query.addChild(name='feature', attrs={'var': 'http://jabber.org/protocol/tune'}) #music
        query.addChild(name='feature', attrs={'var': 'urn:xmpp:avatar:data'}) #user avatars
        query.addChild(name='feature', attrs={'var': 'urn:xmpp:jingle:1'}) #jingle data stream
        query.addChild(name='feature', attrs={'var': 'urn:xmpp:jingle:apps:rtp:1'}) #jingle rtp stream
        query.addChild(name='feature', attrs={'var': 'urn:xmpp:jingle:apps:rtp:audio'}) #jingle audio
        query.addChild(name='feature', attrs={'var': 'urn:xmpp:styling:0'}) #message markup

        iq = xmpp.Iq(to=recipient, typ='result', attrs={'id': id})
        iq.addChild(node=query)
        self.client.send(iq)

    def sendMessage(self, msg, recipient):
        message = xmpp.Message(to=recipient, body=msg)
        #attention = xmpp.Node(tag='attention', attrs={'xmlns': 'urn:xmpp:attention:0'})
        #message.addChild(node=attention)
        self.client.send(message)

    def sendPresenceToAll(self, status, show=None):
        #no 'to' field in a presence means send to all subscribed
        #the caps node contains info about our client and prompts new clients to query our capacities
        caps = xmpp.Node(tag='c', attrs={'xmlns': 'http://jabber.org/protocol/caps', 
                                      'node': XMPPManager.NODE, 'ver':f'{XMPPManager.NODE}v{XMPPManager.VERSION}'})
        pres = xmpp.Presence(status=status, show=show)
        pres.addChild(node=caps)
        self.client.send(pres)

    def sendOnlinePresence(self, recipient, status, show=None):
        pres = xmpp.Presence(to=recipient, status=status, show=show)
        self.client.send(pres)

    def sendOfflinePresence(self, recipient, status=None):
        pres = xmpp.Presence(to=recipient, show='xa', priority=-1, status=status) #a negative priority means offline
        self.client.send(pres) #so the server will (if compliant) store messages and relay them to us when we come back online :)

    def sendOfflinePresenceToAll(self, status=None):
        if status is not None:
            pres = xmpp.Presence(show='xa', priority=-1, status=status) #i also think that defining status as none is dif to not defining it??
        else:
            pres = xmpp.Presence(show='xa', priority=-1) #a negative priority means offline
        self.client.send(pres) #so the server will (if compliant) store messages and relay them to us when we come back online :)

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

        #to respond to capabilities queries we need to register a handler for iq stanzas
        #this isnt part of 'registerHandlers' as it is independent of front end
        self.client.RegisterHandler('iq', self.handleCapIQ, typ='get',
                                    ns='http://jabber.org/protocol/disco#info', makefirst=True)

        self.roster = self.client.getRoster()
        self.updateContacts()

    def closeClient(self):
        self.client.disconnect()
