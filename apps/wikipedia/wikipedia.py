import pyray as pr
import apps.wikipedia.wikipediaManager as wikipediaManager
import textwrap

class App:
    def __init__(self, mstr):
        self.wrapper = textwrap.TextWrapper()
        self.currentArticleText = wikipediaManager.getPage('pizza')
        lines = []
        for line in self.currentArticleText.splitlines():
            wLine = '\n'.join(self.wrapper.wrap(line))
            lines.append(wLine)
        self.text = '\n'.join(lines)

    def draw(self):
        pr.draw_text(self.text, 0, 0, 16, pr.WHITE)

    def update(self):
        pass

    def close(self):
        pass