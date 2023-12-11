import pyray as pr
import textwrap
import menuUtils as mu

class App:
    def __init__(self, mstr):
        self.text = 'Notes'
        self.textwrapper = textwrap.TextWrapper(replace_whitespace=False, width=28)
        
        self.mstr = mstr
        
        mu.associateMaster(mstr)
        self.logger = mu.TextLogger()
        self.logger.start()

    def draw(self):
        wrappedLines = []
        for line in self.text.splitlines():
            wrappedLines.append('\n'.join(self.textwrapper.wrap(line)))

        wrappedText = '\n'.join(wrappedLines)
        pr.draw_text(wrappedText, 0, 0, 14, pr.WHITE)
    
    def update(self):
        self.text = self.logger.getText()

    def close(self):
        self.logger.stop()