import webrtcvad
import pyaudio
import wave
import os
from warnings import simplefilter
import time

simplefilter(action='ignore', category=FutureWarning)

vad = webrtcvad.Vad()
vad.set_mode(2)
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 960
RECORD_SECONDS = 3
BASE_PATH = os.path.dirname(os.path.realpath(__file__))

audio = pyaudio.PyAudio()

info = audio.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
defaultIndex = 0

# show all input devices found.
for i in range(0, numdevices):
    if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))
        if audio.get_device_info_by_host_api_device_index(0, i).get('name') == "default":
            defaultIndex = i

# request the desired device to use as input. If none is selected we use the default.
userInput = input("Select an input device (or hit enter to use default): ")

chosenDevice = defaultIndex
if userInput != '':
    chosenDevice = int(userInput)

print("chosen device: {} - {}".format(chosenDevice, audio.get_device_info_by_host_api_device_index(0, chosenDevice).get('name')))

# start Recording input from selected device
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK, input_device_index=chosenDevice)

instrumentIndex = input("\nSelect an instrument:\n[0] - Piano\n[1] - Guitar\n[2] - Flute\n>")

instrument = ""
match instrumentIndex:
    case "0":
        instrument = "Piano"
    case "1": 
        instrument = "Guitar"
    case "2":
        instrument = "Flute"
    case _:
        print("Please don't be retarded")
        quit()

noteIndex = input("\nSelect a note:\n[0] - C\n[1] - D\n[2] - E\n[3] - F\n[4] - G\n[5] - A\n[6] - B\n>")

note = ""
match noteIndex:
    case "0":
        note = "C"
    case "1": 
        note = "D"
    case "2":
        note = "E"
    case "3":
        note = "F"
    case "4":
        note = "G"
    case "5":
        note = "A"
    case "6":
        note = "B"            
    case _:
        print("Please don't be retarded")
        quit()


print("Chosen note: {}".format(note))

scale = input("\nSelect a scale from 2 to 6: ")

time.sleep(2)
print("ready?")
time.sleep(1)
        
# infinite recording loop
while True:

    try:
        frames = []

        print("recording...")
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        print("finished recording")

        fileName = "{}_{}{}_{}{}".format(instrument, note, scale, time.time(), ".wav")
        waveFile = wave.open(os.path.join(BASE_PATH, instrument, fileName), 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()
    except KeyboardInterrupt:
        print ('Bye bye!')
        break

        
# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()