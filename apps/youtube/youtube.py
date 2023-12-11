import pyray as pr
import apps.youtube.youtubeManager as youtubeManager
import apps.youtube.videoManager as videoManager
import menuUtils as mu
import math

### CLEAN CODE
### RENAME EVERYTHING
### AUTOMATICALLY CLEAN UP FILES AFTER USE
### SYNC AUDIO AND VIDEO
### ADD LOADING SCREEN
### FIX PATHS

class App:
    def __init__(self, mstr):
        self.mstr = mstr
        
        #youtubeManager.downloadVideo('https://www.youtube.com/watch?v=TiC8pig6PGE')

        mu.associateMaster(mstr)
        self.videoPlayer = mu.VideoPlayer()
        #self.videoPlayer.readyFrameExtract('apps/youtube/video.mp4', 'out/')
        #self.extractionDone = False

        self.textLogger = mu.TextLogger()
        self.textLogger.setKeyboard(False)
        #self.videoPlayer.loadVideo('apps/youtube/video.mp4')

        self.beginTerminal()

        #self.RED = (255, 0, 0, 255)
        self.RED = (255, 182, 66, 255)

        self.extractionDone = True
        self.loading = False

        self.blinking = False
        self.blinkTime = 0

        self.commandHistory = ['>hello youtube',  'HELLO JAMES']

        self.processCommand('l TiC8pig6PGE')

    def drawTerminal(self):
        startY = 280
        endY = 100
        pr.draw_text_ex(self.mstr.terminalFont, '>'+self.textLogger.returnText().upper(), (0, 300), 16, 1, self.RED)
        for i, line in enumerate(reversed(self.commandHistory)):
            if line[0] == '>':
                line = 'JAMES-'+line
            pr.draw_text_ex(self.mstr.terminalFont, line, (0, startY-(i*20)), 16, 1, self.RED)

    def drawEye(self, size=15, dotSize=3, angleOffset=0, yMult=1):
        if self.blinking:
            yMult = 0
            if pr.get_time()-self.blinkTime > 0.3:
                self.blinking = False
        elif pr.get_random_value(0, 10000) == 0:
            self.blinking = True
            self.blinkTime = pr.get_time()

        if self.loading:
            angleOffset = pr.get_time()/2
            size=20
            dotSize = 2
            
        centreX = 120
        centreY = 100
        for i in range(0, 8):
            angle = ((i/4)*math.pi)+angleOffset
            pr.draw_circle(int(math.cos(angle)*size)+centreX, (int(math.sin(angle)*size)*yMult)+centreY, dotSize, self.RED)

    def readyVideo(self, url):
        self.videoPlayer.unloadVideo()
        self.commandHistory.append('DOWNLOADING VIDEO...')
        self.startDownload(url)
        self.commandHistory.append('EXTRACTING FRAMES...')
        self.startExraction()
        self.loading = True
        self.state = 'extracting'

    def startDownload(self, url):
        youtubeManager.downloadVideo(f'https://www.youtube.com/watch?v={url}')

    def startExraction(self):
        self.videoPlayer.startExtractingFrames('./apps/youtube/video.mp4', 'out/')
        
    def draw(self):
        self.drawTerminal()
        if self.state == 'playing':
            self.videoPlayer.draw()
        else:
            self.drawEye()

    def beginTerminal(self):
        self.state = 'terminal'
        self.textLogger.start()

    def processCommand(self, entry):
        command, *arguments = entry.split(' ')
        self.commandHistory.append('>'+entry)
        if command == 'hello':
            self.commandHistory.append('HELLO JAMES')
        elif command == 'p':
            self.state = 'playing'
            self.videoPlayer.loadVideo('apps/youtube/video.mp4')
            self.videoPlayer.playVideo()
        elif command == 'load' or command == 'l':
            self.commandHistory.append('LOADING VIDEO...')
            self.readyVideo('https://youtube.com/watch?v='+arguments[0])
        elif command == 'restart' or command=='rst':
            #self.videoPlayer.startTime = pr.get_time()
            self.videoPlayer.restartVideo()
        elif command == 'a':
            self.processCommand('l WEGzvZ85dgs')
        elif command=='seek' or command=='s':
            pass

    def update(self):
        videoPlayerStatus = self.videoPlayer.update()
        if self.loading:
            if self.state == 'extracting':
                self.loading = videoPlayerStatus
                if not self.loading:
                    self.state = 'playing'
                    self.commandHistory.append('PLAYING')
        else:
            if not videoPlayerStatus:
                self.state = 'not playing'
            if '\n' in self.textLogger.getText():
                self.processCommand(self.textLogger.getText()[:-1])
                self.textLogger.reset()

    def close(self):
        self.videoPlayer.unloadVideo()
        self.videoPlayer.close()