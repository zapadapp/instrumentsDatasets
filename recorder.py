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
RECORD_SECONDS = 2
BASE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "DataTrain")

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

note = input("\nInsert note (format: C4, C#4 or C-4):>")

print("Chosen note: {}".format(note))

# checking if path exists for that note
exists = os.path.exists(os.path.join(BASE_PATH, instrument, note))
if not exists:
    os.makedirs(os.path.join(BASE_PATH, instrument, note))

# infinite recording loop
while True:

    try:
        frames = []

        print("recording...")
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        print("finished recording")

        fileName = "{}_{}_{}{}".format(instrument, note, time.time(), ".wav")
        waveFile = wave.open(os.path.join(BASE_PATH, instrument, note, fileName), 'wb')
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