import pyray as pr
import xmpp

class App:
    def __init__(self, mstr):
        self.mstr = mstr

    def handleMessage(self, con, event):
        print(event.getType())
        print(event.getBody())

    def update(self):
        pass

    def draw(self):
        pass

    def close(self):
        pass
