import subprocess
from sound import Sound
import sounddevice  as sd
from pydub import AudioSegment,generators
import simpleaudio
from pydub.playback import _play_with_simpleaudio
from scipy.io import wavfile
import time
import threading
from tkinter import *
subprocess.STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
class main():
    def __init__(self):
        self.defalut = 0
        now_volume = Sound.current_volume()
        Sound.volume_set(50)
        self.thread = threading.Thread(target = self.sing, args = (self.defalut,))
        self.thread.start()
        self.first_default()
        
        #self.start_control()
    def sing(self,dbfs):
        self.singing = True
        self.sound = generators.Sine(440).to_audio_segment(duration=20000)# AudioSegment.from_wav("test.wav")#
        self.sound = self.match_target_amplitude(self.sound,self.defalut)
        self.playback = simpleaudio.play_buffer(
            self.sound.raw_data, 
            num_channels=self.sound.channels, 
            bytes_per_sample=self.sound.sample_width, 
            sample_rate=self.sound.frame_rate
        )
##        while self.singing:
##            pass
        # end playback after 3 seconds
    def match_target_amplitude(self, sound, target_dBFS):
        change_in_dBFS = target_dBFS - sound.dBFS
        return sound.apply_gain(change_in_dBFS)
    def first_default(self):
        self.master = Tk()
        self.master.title('調整聲音')
        self.master.geometry("250x125")
        self.w = Label(self.master, text='調整你的聲音大小')
        self.w.pack()
        self.w = Scale(self.master, from_=-50, to=10, orient=HORIZONTAL,command=self.update)
        self.w.set(self.defalut)
        self.w.pack(fill = X)
        button1 = Button(self.master, text='確定',height = 5,width = 10)
        button1.bind("<ButtonRelease>",self.comfrim)
        button1.pack()
        print(self.w.get())
        mainloop()
    def update(self,event):
        self.playback.stop()
        self.sound = self.match_target_amplitude(self.sound,self.w.get())
        self.playback = simpleaudio.play_buffer(
            self.sound.raw_data, 
            num_channels=self.sound.channels, 
            bytes_per_sample=self.sound.sample_width, 
            sample_rate=self.sound.frame_rate
        )
    def comfrim(self,event):
        print(self.w.get())
        self.playback.stop()
        self.singing = False
        self.defalut = self.w.get()
        self.master.destroy()
        self.control_main()
        
        
    def control_main(self):
        self.master = Tk()
        self.master.title('調整聲音')
        self.master.geometry("300x500")
        self.T = Text(self.master, height=40, width=20)
        S = Scrollbar(self.master)
        self.T.pack(side=LEFT,fill=Y)
        S.pack(side=LEFT, fill=Y)
        S.config(command=self.T.yview)
        self.T.config(yscrollcommand=S.set)
        self.T.insert(END,"Start control volume")
        button1 = Button(self.master, text='調整音量',height = 10,width = 20)
        button1.bind("<ButtonRelease>",self.re_default)
        button1.pack(side=RIGHT)
        self.thread = threading.Thread(target = self.start_control)
        self.thread.start()
        mainloop()
    def re_default(self,event):
        self.continue_ = False
        self.master.destroy()
        self.thread = threading.Thread(target = self.sing, args = (self.defalut,))
        self.thread.start()
        self.first_default()
        
    def get_now_system_DBFS(self):
        sd.default.device[0] =  2
        fs = 1000 # Hz
        length = 1
        recording = sd.rec(frames=fs * length, blocking=True, channels=1)
        wavfile.write("sound1.wav", fs, recording)
        sound = AudioSegment.from_wav("sound1.wav")
        loudness = (sound.dBFS)
        return loudness
    
    def start_control(self):
        now_volume = Sound.current_volume()
        Sound.volume_set(50)
        now_volume = 50
        balance = False
        self.continue_ = True
        try:
            while (self.continue_):
                self.T.see(END)
                now_sound = self.get_now_system_DBFS()
                if(abs(now_sound-self.defalut) >40 ):
                    print("no sound?",now_sound,self.defalut)
                    self.T.insert(END,"\nno sound?")
                    time.sleep(1)
                elif ( now_sound-self.defalut < -2.5):
                    print("volume_up",now_sound,self.defalut)
                    self.T.insert(END,"\nvolume_up")
                    if (now_volume+20 > Sound.current_volume() or not balance):
                        Sound.volume_up()
                        
                elif ( now_sound-self.defalut > 2.5):
                    print("volume_down",now_sound,self.defalut)
                    self.T.insert(END,"\nvolume_down")
                    if (now_volume-20 < Sound.current_volume() or not balance):
                        Sound.volume_down()
                else:
                    print(" balance volume",Sound.current_volume())
                    self.T.insert(END,"\nbalance volume %d"%Sound.current_volume())
                    now_volume = Sound.current_volume()
                    balance = True
                    time.sleep(0.1)
        except:
            pass
#print(sd.query_devices())
main()
