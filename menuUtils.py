import pyray as pr
import math, cv2, subprocess, os

def associateMaster(master):
    global mstr
    mstr = master

class PopUpMenu:
    def __init__(self, menuItems):
        self.menuItemDict = menuItems
        self.menuItemKeys = list(menuItems.keys())
        self.menuItemCount = len(menuItems)
        self.menuIndex = 0

        #self.menubox = pr.load_texture('menubox.png')

    def drawMenuItem(self, menuKey, pos, focus=False):
        green = mstr.HALF_GREEN
        white = mstr.HALF_WHITE
        if focus:
            green = mstr.GREEN
            white = mstr.WHITE
        pr.draw_text_ex(mstr.headingFont, menuKey, (pos[0]+3, pos[1]+15), 30, 1, green)
        pr.draw_text_ex(mstr.headingFont, menuKey, (pos[0], pos[1]+12), 30, 1, white)

    def drawMenu(self):
        #pr.draw_rectangle_rounded(pr.Rectangle(60, 60, 120, 180), 0.5, 2, mstr.WHITE)
        #pr.draw_texture(self.menubox, 60, 70, pr.WHITE)
        pr.draw_rectangle(0, 0, 240, 320, mstr.HALF_BLUE)
        
        """ i = 0
        selectedItem = list(self.menuItems.keys())[self.menuIndex]
        for itemName, itemDetails in self.menuItems.items():
            if itemName == selectedItem:
                pr.draw_text(itemName, 10+i*20, 105, 16, pr.RED)
            else:
                pr.draw_text(itemName, 10+i*20, 105, 16, mstr.BLACK)

            i += 1 """
        
        self.drawMenuItem(self.menuItemKeys[0], (20, 134), focus=True)
        if self.menuItemCount > 1:
            self.drawMenuItem(self.menuItemKeys[1], (10, 218))
            if self.menuItemCount > 2:
                self.drawMenuItem(self.menuItemKeys[-1], (10, 50))
    
    def update(self):
        if pr.is_key_pressed(pr.KEY_UP):
            self.cycleMenuItemsUp()
        if pr.is_key_pressed(pr.KEY_DOWN):
            self.cycleMenuItemsDown()
        
        if pr.is_key_pressed(pr.KEY_ENTER):
            self.menuItemDict[self.menuItemKeys[0]]()

    def cycleMenuItemsDown(self):
        self.menuItemKeys = self.menuItemKeys[1:]+[self.menuItemKeys[0]]

    def cycleMenuItemsUp(self):
        self.menuItemKeys = [self.menuItemKeys[-1]]+self.menuItemKeys[:-1]


class TextLogger:
    def __init__(self, showKeyboard=True):
        self.text = ''

    def setKeyboard(self, state):
        mstr.showKeyboard = state
    
    def start(self):
        mstr.beginTextLogging()
    
    def stop(self):
        mstr.stopTextLogging()

    def returnText(self):
        return self.text+'_'
    
    def reset(self):
        self.text = ''
    
    def getText(self):
        self.update()
        return self.text+'_'
    
    def update(self):
        returnedText = mstr.getLoggedText()
        if returnedText:
            if returnedText == '\b':
                self.text = self.text[:-1]
            else:
                if pr.is_key_down(pr.KEY_RIGHT_SHIFT):
                    print('yay')
                    returnedText = returnedText.upper()
                self.text += returnedText

class TextEntryDialogue:
    textLogger = TextLogger()

    def __init__(self, prompt):
        self.prompt = prompt
        self.completed = False

    def focus(self):
        TextEntryDialogue.textLogger.reset()
        TextEntryDialogue.textLogger.start()
        self.completed = False

    def unfocus(self):
        TextEntryDialogue.textLogger.stop()

    def draw(self):
        pr.draw_rectangle_rounded(pr.Rectangle(10, 115, 220, 60), 0.5, 3, mstr.LIGHT_BLUE)
        pr.draw_rectangle_rounded(pr.Rectangle(15, 145, 210, 20), 0.5, 3, mstr.WHITE)

        pr.draw_text_ex(mstr.headingFont, self.prompt, (15, 120), 20, 1, mstr.WHITE)

        pr.draw_text_ex(mstr.uiFont, TextEntryDialogue.textLogger.returnText(), (15, 150), 16, 1, mstr.BLACK)
    
    def update(self):
        if not self.completed:
            TextEntryDialogue.textLogger.update()
            if pr.is_key_pressed(pr.KEY_ENTER):
                self.completed = True
        
    def getResponse(self):
        if self.completed:
            return TextEntryDialogue.textLogger.returnText()
        else:
            return None
        
class YesNoDialogue:
    def __init__(self, prompt):
        self.prompt = prompt
        self.response = None
    
    def draw(self):
        pr.draw_rectangle_rounded(pr.Rectangle(10, 115, 220, 60), 0.5, 3, mstr.LIGHT_BLUE)
        pr.draw_rectangle_rounded(pr.Rectangle(15, 145, 210, 20), 0.5, 3, mstr.WHITE)

        pr.draw_text_ex(mstr.headingFont, self.prompt, (15, 120), 20, 1, mstr.WHITE)

        pr.draw_text_ex(mstr.uiFont, 'YES/NO', (15, 150), 16, 1, mstr.BLACK)

    def update(self):
        if pr.is_key_pressed(pr.KEY_BACKSPACE):
            self.response = False
        elif pr.is_key_pressed(pr.KEY_ENTER):
            self.response = True

    def getResponse(self):
        return self.response
    
class VideoPlayer:
    def __init__(self):
        self.state = None
        self.musicStream = None
        self.currentFrameTexture = None
        self.frameCount = 0

    def startExtractingFrames(self, videoPath, outputPath):
        self.frameI = 0
        self.count = 0
        self.videoPath = videoPath
        print(os.getcwd()+videoPath)
        self.outputPath = outputPath
        #os.getcwd()+
        self.cap = cv2.VideoCapture(videoPath)
        self.state = 'extracting'

    def extractNextFrame(self):
        #print(self.frameI)
        #print(self.count)
        success, image = self.cap.read()
        print(self.state)
        print(success)
        if success:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.count)
            image = cv2.resize(image, (240, 135))
            #print(f'{os.getcwd()}/{self.outputPath}frame{self.frameI}.png')
            cv2.imwrite(f'{os.getcwd()}/{self.outputPath}frame{self.frameI}.png', image)
            self.count += 5
            self.frameI += 1
            return True
        else:
            print('false')
            self.cap.release()
            self.frameCount = self.frameI
            return False
        

    def extractFrames(self, videoPath, outputPath, callback=None):
        cap = cv2.VideoCapture(videoPath)
        #success,image = vidcap.read()
        count = 0
        i = 0
        while cap.isOpened():
            print(i)
            success, image = cap.read()
            if success:
                cap.set(cv2.CAP_PROP_POS_FRAMES, count)
                #image = cv2.resize(image, (0, 0), fx = 0.375, fy = 0.375)
                print(f'{os.getcwd()}/{outputPath}frame{i}.png')
                cv2.imwrite(f'{os.getcwd()}/{outputPath}frame{i}.png', image)
                count += 5
                i += 1
            else:
                cap.release()
                break
        self.frameCount = i
        if callback is not None:
            callback()
    
    def extractAudio(self, videoPath, outputPath):
        #videoPath = os.getcwd()+'/'+videoPath
        #outputPath = os.getcwd()+'/'+outputPath
        print(outputPath)
        print(videoPath, outputPath)
        newName = '/'.join(outputPath.split('/')[:-1])+'/audio.mp3'
        print(newName)
        command = f'"C:/ffmpeg/bin/ffmpeg.exe" -y -i "{videoPath}" -ab 160k -ac 2 -ar 44100 -vn "{newName}"'

        subprocess.call(command, shell=True)
        print('done')
    
    def loadVideo(self, videoPath):
        pr.init_audio_device()
        #self.extractFrames(videoPath, 'out/')
        #self.extractAudio(videoPath, 'out/')
        audioPath = 'out/audio.mp3'
        self.musicStream = pr.load_music_stream(audioPath)
        pr.play_music_stream(self.musicStream)
        self.framesPath = 'out'

    def unloadVideo(self):
        if self.musicStream is not None:
            pr.unload_music_stream(self.musicStream)
        if self.currentFrameTexture is not None:
            pr.unload_texture(self.currentFrameTexture)
            self.currentFrameTexture = None
        
        for i in range(self.frameCount):
            os.remove(f'{os.getcwd()}/out/frame{i}.png')
        
        try:
            os.remove(f'{os.getcwd()}/out/audio.mp3')
        except FileNotFoundError:
            pass

        self.state = None
        self.musicStream = None
        self.currentFrameTexture = None
        self.frameCount = 0

    def restartVideo(self):
        pr.seek_music_stream(self.musicStream, 0)
        self.startTime = pr.get_time()
        self.currentFrame = 0
        self.currentFrameTexture = None

    def playVideo(self):
        self.startTime = pr.get_time()
        self.currentFrame = 0
        self.currentFrameTexture = None
        pr.play_music_stream(self.musicStream)

    def update(self):
        if self.state == 'playing':
            self.oldFrame = self.currentFrame
            self.currentFrame = math.floor((pr.get_time()-self.startTime)/0.166667)
            if self.currentFrame < self.frameCount:
                if self.currentFrame != self.oldFrame:
                    if self.currentFrameTexture is not None:
                        pr.unload_texture(self.currentFrameTexture)
                    self.currentFrameTexture = pr.load_texture(f'out/frame{self.currentFrame}.png')
                pr.update_music_stream(self.musicStream)
            else:
                return False
        elif self.state == 'extracting':
            if not self.extractNextFrame():
                self.extractAudio('./apps/youtube/video.mp4', './out/audio.mp3')
                self.loadVideo('./out')
                self.startTime = pr.get_time()
                self.currentFrame = 0
                self.currentFrameTexture = None
                self.state = 'playing'
                self.paused = True
                return False
            
        return True

    def draw(self):
        if self.currentFrameTexture is not None:
            pr.draw_texture(self.currentFrameTexture, 0, 0, mstr.WHITE)

    def close(self):
        pr.close_audio_device()
