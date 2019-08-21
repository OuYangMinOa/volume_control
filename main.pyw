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
        self.defalut = 0 # default dbfs
        now_volume = Sound.current_volume() 
        Sound.volume_set(50) # set volume 50
        self.thread = threading.Thread(target = self.sing, args = (self.defalut,))  
        self.thread.start()  # start bee ~~~
        self.first_default()  # gui
        
        #self.start_control()
    def sing(self,dbfs): # the bee sound
        self.singing = True
        self.sound = generators.Sine(440).to_audio_segment(duration=20000) # bee~~~
        self.sound = self.match_target_amplitude(self.sound,self.defalut)  # change dbfs
        self.playback = simpleaudio.play_buffer(  # play bee ~~~
            self.sound.raw_data, 
            num_channels=self.sound.channels, 
            bytes_per_sample=self.sound.sample_width, 
            sample_rate=self.sound.frame_rate
        ) 
    def match_target_amplitude(self, sound, target_dBFS):
        change_in_dBFS = target_dBFS - sound.dBFS
        return sound.apply_gain(change_in_dBFS) # change dBFS
    def first_default(self):
        # Tkinter
        self.master = Tk()
        self.master.title('調整聲音') # title
        self.master.geometry("250x125")
        # Label
        self.w = Label(self.master, text='調整你的聲音大小')
        self.w.pack()
        # Scale
        self.w = Scale(self.master, from_=-50, to=10, orient=HORIZONTAL,command=self.update)
        self.w.set(self.defalut)
        self.w.pack(fill = X)
        # button1
        button1 = Button(self.master, text='確定',height = 5,width = 10)
        button1.bind("<ButtonRelease>",self.comfrim)
        button1.pack()
        # start loop
        mainloop()
    def update(self,event):  # Scale change
        self.playback.stop()  # stop bee~~
        self.sound = self.match_target_amplitude(self.sound,self.w.get()) # change dbfs
        self.playback = simpleaudio.play_buffer(  # restart bee~~
            self.sound.raw_data, 
            num_channels=self.sound.channels, 
            bytes_per_sample=self.sound.sample_width, 
            sample_rate=self.sound.frame_rate
        )
    def comfrim(self,event): # confirm button1 pressed
        print(self.w.get())
        self.playback.stop() # stop bee~~
        self.singing = False
        self.defalut = self.w.get() # get the defalut dbfs
        self.master.destroy() # kill Tk
        self.control_main() # start control system volume
        
        
    def control_main(self): # control system volume
        # Tlk
        self.master = Tk()
        self.master.title('調整聲音')
        self.master.geometry("300x500")
        # Text and Scrollbar
        self.T = Text(self.master, height=40, width=20)
        S = Scrollbar(self.master)
        self.T.pack(side=LEFT,fill=Y)
        S.pack(side=LEFT, fill=Y)
        S.config(command=self.T.yview)
        self.T.config(yscrollcommand=S.set)
        self.T.insert(END,"Start control volume")
        # button
        button1 = Button(self.master, text='調整音量',height = 10,width = 20)
        button1.bind("<ButtonRelease>",self.re_default)
        button1.pack(side=RIGHT)
        # control threading
        self.thread = threading.Thread(target = self.start_control)
        self.thread.start()
        # start loop 
        mainloop()
    def re_default(self,event): # reinitialization 
        self.continue_ = False # stop control system volume
        self.master.destroy() # kill Tk
        self.thread = threading.Thread(target = self.sing, args = (self.defalut,)) #  the bee sound
        self.thread.start()
        self.first_default() # gui
        
    def get_now_system_DBFS(self):
        sd.default.device[0] =  2  # the system sound (maybe not 2
        fs = 1000 # Hz
        length = 1 # s
        recording = sd.rec(frames=fs * length, blocking=True, channels=1) # get system sound
        wavfile.write("sound1.wav", fs, recording) # write
        sound = AudioSegment.from_wav("sound1.wav") # read
        loudness = (sound.dBFS) # get dbfs
        return loudness
    
    def start_control(self):
        now_volume = Sound.current_volume() 
        Sound.volume_set(50)
        now_volume = 50
        balance = False # if balance = True
        self.continue_ = True # continue control
        try:
            while (self.continue_):
                self.T.see(END) # srollbsr goes end
                now_sound = self.get_now_system_DBFS() # get now system dbfs
                if(abs(now_sound-self.defalut) >40 ): # no sound ?
                    print("no sound?",now_sound,self.defalut)
                    self.T.insert(END,"\nno sound?")
                    time.sleep(1)
                elif ( now_sound-self.defalut < -2.5): # need volume_up
                    print("volume_up",now_sound,self.defalut)
                    self.T.insert(END,"\nvolume_up")
                    if (now_volume+20 > Sound.current_volume() or not balance):
                        Sound.volume_up()
                        
                elif ( now_sound-self.defalut > 2.5): # need volume_down
                    print("volume_down",now_sound,self.defalut)
                    self.T.insert(END,"\nvolume_down")
                    if (now_volume-20 < Sound.current_volume() or not balance):
                        Sound.volume_down()
                else: # it balance Take a rest ~.~
                    print(" balance volume",Sound.current_volume())
                    self.T.insert(END,"\nbalance volume %d"%Sound.current_volume())
                    now_volume = Sound.current_volume()
                    balance = True
                    time.sleep(0.1)
        except:
            pass
print(sd.query_devices()) # find Stereo mix ( Mine is 2
main()
