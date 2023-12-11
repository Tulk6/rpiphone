import apps.youtube.videoManager as videoManager
#import videoManager
import pytube, subprocess

def downloadVideo(url):
    yt = pytube.YouTube(url)
    yt.streams.get_by_itag(18).download(output_path='apps/youtube', filename='video.mp4')

class YoutubeManager:
    def __init__(self):
        pass

    def loadVideo(self, url):
        self.yt = pytube.YouTube(url)
        #print(self.yt.streams.filter(res='144p'))
        #print(self.yt.streams.filter(only_audio=True))
        self.yt.streams.get_by_itag(18).download(output_path='apps/youtube', filename='video.mp4')
        #self.yt.streams.get_by_itag(139).download(output_path='apps/youtube', filename='audio.mp4')

    def processVideo(self, stream, path):
        print('here')
        videoManager.extractFrames('apps/youtube/video.mp4')
        videoManager.extractAudio('apps/youtube/video.mp4')

    def loadAudio(self, url):
        self.yt = pytube.YouTube(url, on_complete_callback=self.processAudio)
        #print(self.yt.streams.filter(res='144p'))
        #print(self.yt.streams.filter(only_audio=True))
        #self.yt.streams.get_by_itag(18).download()
    
    def processAudio(self, stream, path):
        videoManager.extractAudio('apps/youtube/video.mp4')

