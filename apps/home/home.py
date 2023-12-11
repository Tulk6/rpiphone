import pyray as pr
import datetime, os, tomllib

class AppMenuItem:
    def __init__(self, master, appTarget, name, pos, visible=True):
        self.mstr = master
        self.appTarget = appTarget
        self.icon = pr.load_texture('apps/'+appTarget+'/icon.png')
        self.name = name
        self.pos = pos
    
    def draw(self, pos, focus=False):
        green = self.mstr.mstr.GREEN
        white = self.mstr.mstr.WHITE
        if focus:
            pr.draw_text_ex(self.mstr.mstr.headingFont, self.name, (pos[0]+76, pos[1]+15), 44, 1, green)
            pr.draw_text_ex(self.mstr.mstr.headingFont, self.name, (pos[0]+73, pos[1]+12), 44, 1, white)
        #else:
            #green = self.mstr.mstr.HALF_GREEN
            #white = self.mstr.mstr.HALF_WHITE
        pr.draw_texture(self.icon, pos[0], pos[1], white)

    def close(self):
        pr.unload_texture(self.icon)
        del self
        
class App:
    def __init__(self, manager):
        self.currDateTime = datetime.datetime.now().strftime("%H:%M, %d %B")
        self.mstr = manager

        self.bar = pr.load_texture('apps/home/bar.png')
        self.wallpaper = pr.load_texture('apps/home/follow.png')

        self.appItems = []
        self.loadAppItems()

    def loadAppItems(self):
        for folder in [i for i in os.listdir('apps') if i != 'home']:
            with open('apps/'+folder+'/index.toml', 'rb') as file:
                data = tomllib.load(file)
                self.appItems.append(AppMenuItem(self, folder, data['manifest']['appName'], (0,50)))

        print(self.appItems)

    def cycleAppItemsDown(self):
        self.appItems = [self.appItems[-1]]+self.appItems[:-1]

    def cycleAppItemsUp(self):
        self.appItems = self.appItems[1:]+[self.appItems[0]]
        
    def draw(self):
        pr.draw_texture(self.wallpaper, 0, 0, pr.WHITE)

        #pr.draw_text_ex(self.mstr.headingFontOblique, 'Media', (145, 60), 18, 1, self.mstr.WHITE)
        
        pr.draw_texture(self.bar, 10, 5, pr.WHITE)
        pr.draw_text_ex(self.mstr.uiFont, f'Welcome :) {self.currDateTime}', (15, 8), 16, 0.5, self.mstr.WHITE)

        self.appItems[0].draw((2, 50)) #item above
        self.appItems[1].draw((20, 134), focus=True) #current item
        self.appItems[2].draw((2, 218)) #item below

    def update(self):
        if pr.is_key_pressed(pr.KEY_UP):
            self.cycleAppItemsDown()
        elif pr.is_key_pressed(pr.KEY_DOWN):
            self.cycleAppItemsUp()

        if pr.is_key_pressed(pr.KEY_ENTER):
            self.mstr.loadApp(self.appItems[1].appTarget)

    def close(self):
        for appItem in self.appItems:
            appItem.close()

        pr.unload_texture(self.bar)
        pr.unload_texture(self.wallpaper)
