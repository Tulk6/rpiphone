import os, importlib.util, json
import pyray as pr

#TO DO:
#   - dyanmic loading/unloading of Unicode codepoints 

class MainWindow:
    def __init__(self):
        pr.init_window(240, 320, 'hello')
        #pr.set_target_fps(30)

        self.loadDefaults()   

        self.textLogging = False
        self.textKeys = {pr.KEY_KP_0: 0,
                         pr.KEY_KP_1: 1,
                         pr.KEY_KP_2: 2,
                         pr.KEY_KP_3: 3,
                         pr.KEY_KP_4: 4,
                         pr.KEY_KP_5: 5,
                         pr.KEY_KP_6: 6,
                         pr.KEY_KP_7: 7,
                         pr.KEY_KP_8: 8,
                         pr.KEY_KP_9: 9}
        self.keyTranslation = json.load(open('textKeys.json'))

        self.app = None
        self.showKeyboard = True
        self.loadApp('home')

    def loadDefaults(self):
        self.uiFont = pr.load_font_ex('ui/fonts/LSANS.ttf', 16, None, 0)
        #self.headingFont = pr.load_font_ex('ui/fonts/yeoman/YeomanJack.otf', 32, None, 0)
        self.headingFontOblique = pr.load_font_ex('ui/fonts/YeomanJackTwoToneItalic.otf', 30, None, 0)
        self.headingFont = pr.load_font_ex('ui/fonts/toxigenesis.otf', 44, None, 0)
        self.monoFont = pr.load_font_ex('ui/fonts/consola.ttf', 14, None, 0)
        self.terminalFont = pr.load_font_ex('ui/fonts/courbd.ttf', 16, None, 0)
        #self.lcdFont = pr.load_font_ex('ui/fonts/lcddot_tr.ttf', 18, None, 0)
        #self.euroFont = pr.load_font_ex('ui/fonts/Eurocine.otf', 18, None, 0)
        self.pixelFont = pr.load_font_ex('ui/fonts/invasion2000.regular.ttf', 18, None, 0)
        #self.fontOutline = pr.load_font_ex('ui/fonts/yeoman/YeomanJack3D.otf', 60, None, 0)

        self.WHITE = (255, 255, 255, 255)
        self.BLACK = (0, 0, 0, 255)
        self.CREAM = (224, 201, 106, 255)
        self.GREEN = (0, 128, 2, 255)

        self.LIGHT_BLUE = (100, 176, 185, 255)
        self.DARK_BLUE = (41, 71, 106, 255)

        self.HALF_WHITE = (255, 255, 255, 120)
        self.HALF_GREEN = (0, 128, 2, 120)
        self.HALF_BLUE = (100, 176, 185, 120)
        self.MORE_BLUE = (100, 176, 185, 200)

    def importLibraryFromFile(self, filePath):
        spec = importlib.util.spec_from_file_location('appLib', filePath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    
        return module

    def loadApp(self, appName):
        if self.app is not None: #if a current app is open, its close fuction should be run
            self.app.close()
        if os.path.exists('apps/'+appName):
            self.appLib = self.importLibraryFromFile('apps/'+appName+'/'+appName+'.py')
            self.app = self.appLib.App(self)

    def beginTextLogging(self):
        self.textLogging = True
        self.currentCodeString = ''
        self.enteredText = None
    
    def stopTextLogging(self):
        self.textLogging = False

    def drawKeyboard(self):
        pr.draw_rectangle(10, 200, 220, 40, self.LIGHT_BLUE)

        if self.currentCodeString == '':
            pr.draw_text_ex(self.uiFont, '0: a-j \t\t 1: k-t \t\t 2: u-z', (40, 210), 16, 1, self.WHITE)
        elif self.currentCodeString == '0':
            pr.draw_text_ex(self.uiFont, '0:a 1:b 2:c 3:d 4:e 5:f 6:g \n7:h 8:i 9:j', (20, 210), 16, 1, self.WHITE)
        elif self.currentCodeString == '1':
            pr.draw_text_ex(self.uiFont, '0:k 1:l 2:m 3:n 4:o 5:p 6:q \n7:r 8:s 9:t', (20, 210), 16, 1, self.WHITE)
        elif self.currentCodeString == '2':
            pr.draw_text_ex(self.uiFont, '0:u 1:v 2:w 3:x 4:y 5:z', (20, 210), 16, 1, self.WHITE)


    def logText(self):
        for key in self.textKeys.keys():
            if pr.is_key_pressed(key):
                self.currentCodeString += str(self.textKeys[key])
        
        if pr.is_key_pressed(pr.KEY_LEFT):
            self.currentCodeString = ''
        
        if pr.is_key_pressed(pr.KEY_RIGHT):
            self.currentCodeString = ''
            self.enteredText = '\b'
        
        if len(self.currentCodeString) >= 2:
            try:
                self.enteredText = self.keyTranslation[self.currentCodeString]
            except KeyError:
                pass
            self.currentCodeString = ''

    def getLoggedText(self):
        if self.enteredText:
            ret = self.enteredText
            self.enteredText = None
            return ret
        return None
            
    def mainloop(self):
        while not pr.window_should_close():
            #print(pr.get_fps())
            self.app.update()

            pr.begin_drawing()
            pr.clear_background(pr.BLACK)

            self.app.draw()

            if self.textLogging and self.showKeyboard:
                self.drawKeyboard()

            pr.end_drawing()

            if pr.is_key_pressed(pr.KEY_TAB):
                self.loadApp('home')

            if self.textLogging:
                self.logText()

        self.app.close()
        pr.close_window() 

window = MainWindow()
window.loadApp('chat')
window.mainloop()

###