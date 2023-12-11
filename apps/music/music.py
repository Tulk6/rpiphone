import pyray as pr
import tomllib, PIL.Image, requests, threading, time, os
import apps.music.musicManager as musicManager
import menuUtils as mu

class App:
    def __init__(self, mstr):
        self.mstr = mstr
        mu.associateMaster(mstr)

        self.popUpMenu = mu.PopUpMenu({'Switch Screen': self.switchScreen, 'Playlists': self.enterPlaylistMenu,
                                       'Search': self.beginSearching})

        self.loadSettings()

        self.loadSkin('custom')

        self.musicManager = musicManager.MusicManager(self.settings['api']['key'])
        self.musicManager.loadLibrary('user/music/')

        self.textEntry = mu.TextEntryDialogue('Song Name')

        self.volume = 1
        self.pan = .5

        self.screen = 'main'
        self.menuVisible = False
        self.libraryIndex = 0
        self.playlistMenuIndex = 0

        self.playlistIndex = 0

        self.searchResultsIndex = 0

        #self.defaultAlbumCover = pr.load_texture_from_image(pr.gen_image_color(174, 174, self.mstr.GREEN))
        #self.currentAlbumCover = None #the current album texture, None if none loaded
        #self.loadAlbumTexture = False #if pr needs to load texture
        #print(self.musicManager.playlits)
        #self.musicManager.playSong('Mirage')
        #self.musicManager.queuePlaylist('new playlist')
        #self.musicManager.playNextSongInQueue()
        #self.musicManager.pause()
        #print(self.musicManager.getCurrentSongData()['track']['album']['image'])
        #PIL.Image.open(requests.get(self.musicManager.getCurrentSongData()['track']['album']['image'][0]['#text'], stream=True).raw).show()

    def loadSettings(self):
        with open('apps/music/index.toml', 'rb') as file:
            self.settings = tomllib.load(file)['settings']

    def loadSkin(self, name):
        self.stInfo = pr.load_texture('apps/music/skins/'+name+'/info.png')
        self.stSeek = pr.load_texture('apps/music/skins/'+name+'/seek.png')
        self.stPlaylist = pr.load_texture('apps/music/skins/'+name+'/playlist.png')
        self.stLibrary = pr.load_texture('apps/music/skins/'+name+'/library.png')

    def threadGetAlbumCover(self):
        self.coverThread = threading.Thread(target=self.getAlbumCover)
        self.coverThread.start()

    def getAlbumCover(self):
        if self.musicManager.currentSongObject is not None:
            cover = PIL.Image.open(requests.get(self.musicManager.getCurrentSongData()['track']['album']['image'][2]['#text'], stream=True).raw)
            cover.save('apps/music/cover.png', 'PNG')
            if self.currentAlbumCover is not None:
                pr.unload_texture(self.currentAlbumCover)
                self.currentAlbumCover = None
            self.loadAlbumTexture = True

    def drawSongInfo(self):
        # if self.currentAlbumCover is None:
        #     pr.draw_texture(self.defaultAlbumCover, 33, 10, self.mstr.WHITE)
        # else:
        #     pr.draw_texture(self.currentAlbumCover, 33, 10, self.mstr.WHITE)
        #volumeBarWidth = 88
        #volumeBarStart = 10

        pr.draw_rectangle(10+int(88*self.volume), 86, 4, 8, self.mstr.BLACK) #volume indicator 
        pr.draw_rectangle(10+int(88*(1-self.pan)), 101, 4, 8, self.mstr.BLACK) #pan indicator (pan is reversed)


        if self.musicManager.musicStream is not None:
            scrollSpeed = 2
            infoText = (f'{self.musicManager.currentSongObject.title}'
                         f' - {self.musicManager.currentSongObject.album}'
                         f' - {self.musicManager.currentSongObject.artist}'
                         '     ')
            #titleWidth = pr.measure_text(infoText, 18)
            startOffset = int(pr.get_time()*scrollSpeed) % len(infoText) #make it pause for a second on name!
            #print('startOffset', startOffset)
            endOffset = (startOffset + 13) % len(infoText)
            #print('endOffset', endOffset)
            if endOffset < startOffset:
                shortened = infoText[startOffset:] + infoText[:endOffset]
            else:
                shortened = infoText[startOffset:endOffset]
            pr.draw_text_ex(self.mstr.pixelFont, shortened, (84, 28), 18, 1, self.mstr.BLACK)

            timePlayed = self.musicManager.getFormatedTimePlayed()
            pr.draw_text(timePlayed, 18, 40, 22, self.mstr.BLACK)

            #seek bar start (10, 30) width 219
            pr.draw_rectangle(10+int(219*self.musicManager.getProportionPlayed()), 148, 4, 8, self.mstr.BLACK) #seek indicator

    def drawPlaylist(self):
        for i, song in enumerate(self.musicManager.history+self.musicManager.queue):
            drawY = 195 + i*20
            if i == len(self.musicManager.history)-1: #sorta wacky but the last song in history is currently playing so highlights current song
                textColour = self.mstr.WHITE #highlightinh based on name didnt work cos of duplicates
            else:
                textColour = self.mstr.BLACK
            if i == self.playlistIndex:
                pr.draw_rectangle(5, drawY-3, 220, 20, (179, 200, 216, 255)) #custom colour
            infoString = f'{i+1}. {song.title} - {song.artist}'
            if len(infoString) > 27:
                infoString = infoString[:24]+'...'
            pr.draw_text_ex(self.mstr.monoFont, infoString, (10, drawY), 
                            14, 1, textColour)
            
    def drawMusicLibrary(self):
        pr.draw_texture(self.stLibrary, 0, 0, self.mstr.WHITE)
        for (i, song) in enumerate(self.musicManager.librarySongList):
            if i == self.libraryIndex:
                textColour = self.mstr.WHITE
            else:
                textColour = self.mstr.BLACK
            drawY = 10 + i*20
            infoString = f'{i+1}. {song.title} - {song.artist}'
            if len(infoString) > 27:
                infoString = infoString[:24]+'...'
            pr.draw_text_ex(self.mstr.monoFont, infoString, (10, drawY), 
                            14, 1, textColour)
            
    def switchScreen(self):
        if self.screen == 'main': #switches between screens, called from popupmenu
            self.screen = 'library'
        else:
            self.screen = 'main'

        self.textEntry.unfocus()
        self.menuVisible = False #hides the popupmenu if it is up

    def enterPlaylistMenu(self):
        self.textEntry.unfocus()
        self.menuVisible = False
        self.screen = 'playlist'

    def beginSearching(self):
        self.menuVisible = False
        self.screen = 'search'
        self.textEntry.focus()

    def drawPlaylistMenu(self):
        pr.draw_texture(self.stLibrary, 0, 0, self.mstr.WHITE)
        for (i, playlist) in enumerate(list(self.musicManager.playlists.keys())):
            if i == self.playlistMenuIndex:
                textColour = self.mstr.WHITE
            else:
                textColour = self.mstr.BLACK
            drawY = 10 + i*20
            infoString = f'{i}. {playlist}'
            if len(infoString) > 27:
                infoString = infoString[:24]+'...'
            pr.draw_text_ex(self.mstr.monoFont, infoString, (10, drawY), 
                            14, 1, textColour)
            
    def drawSearchResults(self):
        pr.draw_texture(self.stLibrary, 0, 0, self.mstr.WHITE)
        for (i, song) in enumerate(self.searchResults):
            if i == self.searchResultsIndex:
                textColour = self.mstr.WHITE
            else:
                textColour = self.mstr.BLACK
            drawY = 10 + i*20
            infoString = f'{i+1}. {song.title} - {song.artist}'
            if len(infoString) > 27:
                infoString = infoString[:24]+'...'
            pr.draw_text_ex(self.mstr.monoFont, infoString, (10, drawY), 
                            14, 1, textColour)
    
    def draw(self):
        if self.screen == 'main':
            #pr.draw_texture(self.bgTexture, 0, 0, self.mstr.WHITE)
            pr.draw_texture(self.stInfo, 0, 0, self.mstr.WHITE) #background panels
            pr.draw_texture(self.stSeek, 0, 120, self.mstr.WHITE)
            pr.draw_texture(self.stPlaylist, 0, 180, self.mstr.WHITE)

            #pr.draw_text_ex(self.mstr.headingFontOblique, 'Music', (0, 0), 30, 1, self.mstr.WHITE)

            self.drawSongInfo()
            self.drawPlaylist()
        elif self.screen == 'library':
            self.drawMusicLibrary()
        elif self.screen == 'playlist':
            self.drawPlaylistMenu()
        elif self.screen == 'search':
            pr.draw_texture(self.stLibrary, 0, 0, self.mstr.WHITE)
            self.textEntry.draw()
        elif self.screen == 'search results':
            self.drawSearchResults()
        
        if self.menuVisible:
            self.popUpMenu.drawMenu()

    def update(self):
        self.musicManager.updateStream()

        if pr.is_key_pressed(pr.KEY_RIGHT_SHIFT):
            self.menuVisible = not self.menuVisible

        #arrow keys will control interaction around window and playlist
        #numpad will control volume pan and skipping (plus typing if needed)

        #controlling pan and volume
        if self.screen != 'search':
            if pr.is_key_pressed(pr.KEY_KP_4):
                self.pan = min(1, self.pan+0.1)
                self.musicManager.setPlaybackPan(self.pan)
            elif pr.is_key_pressed(pr.KEY_KP_6):
                self.pan = max(0, self.pan-0.1)
                self.musicManager.setPlaybackPan(self.pan)

            if pr.is_key_pressed(pr.KEY_KP_2):
                self.volume = max(0, self.volume-0.1)
                self.musicManager.setPlaybackVolume(self.volume)
            elif pr.is_key_pressed(pr.KEY_KP_8):
                self.volume = min(1, self.volume+0.1)
                self.musicManager.setPlaybackVolume(self.volume)
            
            if pr.is_key_pressed(pr.KEY_KP_5):
                self.musicManager.togglePlayPause()

            #skipping songs
            if pr.is_key_pressed(pr.KEY_KP_7):
                self.musicManager.previousSong()
            elif pr.is_key_pressed(pr.KEY_KP_9):
                self.musicManager.nextSong()
        if not self.menuVisible:
            if self.screen == 'main' and len(self.musicManager.history+self.musicManager.queue) > 0: #if its less than zero we cant scroll!
                #moving up and down in playlist menu
                if pr.is_key_pressed(pr.KEY_DOWN):
                    self.playlistIndex = (self.playlistIndex+1) % len(self.musicManager.history+self.musicManager.queue)
                elif pr.is_key_pressed(pr.KEY_UP):
                    self.playlistIndex = (self.playlistIndex-1) % len(self.musicManager.history+self.musicManager.queue)

                if pr.is_key_pressed(pr.KEY_LEFT):
                    if self.playlistIndex > len(self.musicManager.history)-1:
                        self.musicManager.queue.pop(self.playlistIndex-len(self.musicManager.history))
                    else:
                        self.musicManager.history.pop(self.playlistIndex)

            elif self.screen == 'library':
                #moving up and down in library
                if pr.is_key_pressed(pr.KEY_DOWN):
                    self.libraryIndex = (self.libraryIndex+1) % self.musicManager.librarySize
                elif pr.is_key_pressed(pr.KEY_UP):
                    self.libraryIndex = (self.libraryIndex-1) % self.musicManager.librarySize

                if pr.is_key_pressed(pr.KEY_LEFT): #left and right arrows add song to end and start of queue respectively
                    self.musicManager.addSongToQueue(self.musicManager.librarySongList[self.libraryIndex])
                elif pr.is_key_pressed(pr.KEY_RIGHT):
                    self.musicManager.addSongNext(self.musicManager.librarySongList[self.libraryIndex])

                if pr.is_key_pressed(pr.KEY_ENTER):
                    self.musicManager.queueAndPlay(self.musicManager.librarySongList[self.libraryIndex])
                
            elif self.screen == 'playlist':
                if pr.is_key_pressed(pr.KEY_DOWN):
                    self.playlistMenuIndex = (self.playlistMenuIndex+1) % len(self.musicManager.playlists.keys())
                elif pr.is_key_pressed(pr.KEY_UP):
                    self.playlistMenuIndex = (self.playlistMenuIndex-1) % len(self.musicManager.playlists.keys())

                if pr.is_key_pressed(pr.KEY_ENTER):
                    self.musicManager.queuePlaylist(list(self.musicManager.playlists.keys())[self.playlistMenuIndex],
                                                    shufflePlaylist=True)
                    self.screen = 'main'

            elif self.screen == 'search':
                self.textEntry.update()
                if self.textEntry.getResponse() is not None:
                    self.searchEntry = self.textEntry.getResponse()
                    print(self.searchEntry)
                    self.textEntry.unfocus()
                    self.searchResults = self.musicManager.getSearchResults(self.searchEntry)
                    print(self.searchResults)
                    self.screen = 'search results'

            elif self.screen == 'search results':
                if pr.is_key_pressed(pr.KEY_DOWN):
                    self.searchResultsIndex = (self.searchResultsIndex+1) % len(self.searchResults)
                elif pr.is_key_pressed(pr.KEY_UP):
                    self.searchResultsIndex = (self.searchResultsIndex-1) % len(self.searchResults)

                if pr.is_key_pressed(pr.KEY_LEFT): #left and right arrows add song to end and start of queue respectively
                    self.musicManager.addSongToQueue(self.searchResults[self.searchResultsIndex])
                elif pr.is_key_pressed(pr.KEY_RIGHT):
                    self.musicManager.addSongNext(self.searchResults[self.searchResultsIndex])

                if pr.is_key_pressed(pr.KEY_ENTER):
                    self.musicManager.queueAndPlay(self.searchResults[self.searchResultsIndex])

        
        if self.menuVisible:
            self.popUpMenu.update()

    def close(self):
        self.musicManager.stop()

        pr.unload_texture(self.stInfo)
        pr.unload_texture(self.stSeek)
        pr.unload_texture(self.stPlaylist)
        pr.unload_texture(self.stLibrary)
