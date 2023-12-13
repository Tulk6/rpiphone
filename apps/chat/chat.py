import pyray as pr
import apps.chat.xmppManager as xmppManager
import menuUtils as mu
import tomllib, yaml

class ChatObject:

    showNames = {None: 'online :D',
                          'xa': 'out D:',
                          'dnd': 'busy :|',
                          'away': 'away :('}
    
    def __init__(self, mstr, targetJid):
        self.mstr = mstr
        self.xmppManager = self.mstr.xmppManager
        self.targetJid = targetJid
        self.contact = self.xmppManager.contacts[self.targetJid]
        self.status = self.contact['status']
        self.show = self.contact['show']
        self.targetName = self.contact['name']

        self.loadChatHistory()

    def loadChatHistory(self):
        self.messages = []
        try:
            with open('apps/chat/chatHistories/'+self.targetJid+'.yaml', 'r') as file:
                #print(file.read())
                #print(yaml.safe_load(file))
                try:
                    for message in yaml.safe_load(file):
                        self.messages.append(message)
                except TypeError: #it seems like reading file b4 hand to see if it is empty makes it so u cannot safe_load??
                    pass #so instead just catching the error
                print(self.messages)
        except FileNotFoundError:
            with open('apps/chat/chatHistories/'+self.targetJid+'.yaml', 'w') as file:
                pass

    def receiveMessageEvent(self, event):
        self.messages.append((self.targetName, event.getBody()))

    def sendMessage(self, msg):
        self.xmppManager.sendMessage(msg, self.targetJid)
        self.messages.append(('You', msg))

    @property
    def formattedShow(self):
        if self.status is None and self.show is None: #an offline presence is None status and Show (available is None show)
            show = 'offline ._.'
        else:
            show = ChatObject.showNames[self.show] #apart from offline/available every other show is unique, so a display string is got from a dictionary

        return show

    @property
    def formattedMessages(self):
        formattedMessages = []
        for sender,body in self.messages:
            formattedMessages.append(f'{sender}: {body}')
        return formattedMessages
    
    def update(self):
        self.contact = self.xmppManager.contacts[self.targetJid]
        self.status = self.contact['status']
        self.show = self.contact['show']

    def close(self):
        output = ''
        for name, message in self.messages:
            output += f'- [{name}, {message}]\n'
        with open('apps/chat/chatHistories/'+self.targetJid+'.yaml', 'w') as file:
            file.write(output)

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

        self.loadChatObjects()

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

    def loadChatObjects(self):
        self.chatObjects = {}
        for jid in self.xmppManager.contactJids:
            self.chatObjects[jid] = ChatObject(self, jid)

        print(self.chatObjects)

    def handlePresence(self, con, event):
        print('-->',self.xmppManager.roster.getShow('jamestulk@jabbers.one'))
        if event.getFrom().getStripped() != self.xmppManager.address:
            self.xmppManager.updateContacts()
            self.chatObjects[event.getFrom().getStripped()].update()
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
            self.chatObjects[event.getFrom().getStripped()].receiveMessageEvent(event)
        elif event.getType() == 'error':
            print('---> ERROR: ', event.getBody())

    def determineDisplayShow(self, contact):
        if contact['status'] is None and contact['show'] is None: #an offline presence is None status and Show (available is None show)
            show = 'offline ._.'
        else:
            show = self.showNames[contact['show']] #apart from offline/available every other show is unique, so a display string is got from a dictionary

        return show
    
    def drawConversation(self, x, y, chatObject):
        pr.draw_rectangle_rounded_lines(pr.Rectangle(x,y, 220, 40), 0.4, 2, 1, self.mstr.WHITE)

        #displayName = f'{contact["name"]} [{jid}]'
        #if len(displayName) > 23:
            #displayName = displayName[:19] + '...]'
        pr.draw_text_ex(self.mstr.uiFont, f'{chatObject.targetName} is {chatObject.formattedShow}', (x+4, y+5), 16, 1, self.mstr.WHITE)

        if chatObject.status is not None:
            pr.draw_text_ex(self.mstr.uiFont, f"Says '{chatObject.status}'", (x+4, y+23), 16, 1, self.mstr.WHITE)

    def loadSettings(self):
        with open('apps/chat/index.toml', 'rb') as file:
            self.settings = tomllib.load(file)['settings']

    def loadAddressBook(self):
        with open('user/address_book/address_book.yaml', 'r') as file:
            self.addressBook = yaml.safe_load(file)

    def startChat(self, jid):
        self.state = 'Chat'
        self.currentChatObject = self.chatObjects[jid]
        self.chatJid = jid
        self.xmppManager.sendOnlinePresence(jid, self.settings['xmpp']['onlineStatus'], show='available')
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
                self.currentChatObject.sendMessage(self.textLogger.text)
                self.textLogger.reset()
            
            if pr.is_key_pressed(pr.KEY_UP):
                self.state = 'Conversations'
                self.textLogger.stop()
                print('yay!')

        #print(self.xmppManager.contacts.getStatus('jamestulk@jabbers.one'))

    def draw(self):
        pr.draw_texture(self.background, 0, 0, pr.WHITE)
        if self.state == 'Conversations': #go through every contact 
            pr.draw_line_ex((10, 40), (240, 40), 4.0, self.mstr.WHITE)
            pr.draw_text_ex(self.pixelFontHeading, 'Conversations', (10, 8), 24, 1, self.mstr.WHITE)
            pr.draw_text_ex(self.mstr.uiFont, '>', (0, 65+(self.conversationIndex*50)), 16, 1, self.mstr.WHITE)
            for i, (jid, chatObject) in enumerate(self.chatObjects.items()):
                self.drawConversation(10, 55+(i*50), chatObject)
        elif self.state == 'Chat':
            pr.draw_line_ex((10, 40), (240, 40), 4.0, self.mstr.WHITE)
            pr.draw_text_ex(self.pixelFontHeading, self.currentChatObject.targetName, (10, 8), 24, 1, self.mstr.WHITE)
            pr.draw_text_ex(self.mstr.uiFont, f'Currently {self.currentChatObject.formattedShow}',
                            (10, 46), 16, 1, self.mstr.WHITE)
            
            pr.draw_rectangle_rounded_lines(pr.Rectangle(10,270, 220, 40), 0.4, 2, 1, self.mstr.WHITE)
            pr.draw_text_ex(self.mstr.uiFont, self.textLogger.getText(), (10, 270), 16, 1, self.mstr.WHITE)

            for i, message in enumerate(reversed(self.currentChatObject.formattedMessages)):
                pr.draw_text_ex(self.mstr.uiFont, message, (10, 250-(12*i)), 16, 1, self.mstr.WHITE)


    def close(self):
        pr.unload_texture(self.background)

        for jid, chatObject in self.chatObjects.items():
            chatObject.close()

        self.xmppManager.sendPresenceToAll(self.settings['xmpp']['offlineStatus'], show='away')
        self.xmppManager.closeClient()
