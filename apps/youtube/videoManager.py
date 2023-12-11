import cv2, os
#import ffmpeg
import subprocess

class VideoManager:
    def __init__(self):
        pass

    def readyVideo(self, path):
        self.path = path
        self.extractFrames(path)
        self.extractAudio(path)

    def clearCache(self):
        path = '/'.join(self.path.split('/')[:-1])+'/audio.mp3'
        os.remove(path)

        for file in os.listdir('apps/youtube/out/'):
            print(file)
            os.remove(file)

    def extractFrames(self, videoPath):
        print(videoPath)
        cap = cv2.VideoCapture(videoPath)
        #success,image = vidcap.read()
        count = 0
        i = 0
        print('frames1')
        while cap.isOpened():
            print(i)
            success, image = cap.read()
            if success:
                print('success')
                count += 5
                i += 1
                cap.set(cv2.CAP_PROP_POS_FRAMES, count)
                #image = cv2.resize(image, (0, 0), fx = 0.375, fy = 0.375)
                cv2.imwrite(f'apps/youtube/out/frame{i}.png', image)
            else:
                cap.release()
                break
        return i
    
    def extractAudio(self, path):
        print(path)
        # input = ffmpeg.input(path)
        # ffmpeg.output(input.audio, 'out.mp3').run()
        path = os.getcwd()+'/'+path
        print(path)
        newName = os.getcwd()+'/out/audio.mp3'
        print(newName)
        command = f'"C:/ffmpeg/bin/ffmpeg.exe" -i "{path}" -ab 160k -ac 2 -ar 44100 -vn "{newName}"'

        subprocess.call(command, shell=True)
        """ newName = '\\'.join(path.split('\\')[:-1])+'\\audio.mp3'
        if os.path.isfile(newName):
            os.remove(newName)
        os.rename(path, newName) """
