import tdt
from win32com.client import Dispatch
import slab
import numpy
import time
from mobile_rack import initialize, get_recording, experiment, create_and_store_file, equalize_loudness, get_drr_recording, select_channel, play
proc = Dispatch('RPco.X')
SAMPLERATE = 48828
slab.set_default_samplerate(SAMPLERATE)
initialize()

sound = slab.Sound.tone(frequency=1000, duration=0.5, level=85, samplerate=48000)

sound.play()

select_channel(11)
play(data=sound)

select_channel(3)
for n in range(0, 16):
    print(n)
    select_channel(n)
    play(data=sound)
    time.sleep(0.5)

"""
speaker = 1
speaker_distance = 343.2
frequency = 800
duration = 5.0
level = 80
rec_channel = 1

proc.SetTagVal('chan_number', speaker)
proc.SoftTrg(1)
print('\n   Multiplexer output channel set to ' + str(speaker))
# setting up playback
slab.set_default_samplerate(48000)
sound = slab.Sound.tone(frequency=frequency, duration=duration, level=level)
data = sound.data.flatten()
proc.SetTagVal('playbuflen', len(data))
proc._oleobj_.InvokeTypes(15, 0x0, 1, (3, 0), ((8, 0), (3, 0), (0x2005, 0)), 'play_data', 0, data)
# setting up recording
proc.SetTagVal('analog_in', rec_channel)
proc.SetTagVal('recbuflen', len(data))
delay = speaker_distance/343.2
proc.SetTagVal('rec_delay', delay*1000)
proc.SoftTrg(2)
time.sleep(delay+duration)
while proc.GetTagVal('recording'):
    time.sleep(0.01)
rec_data = proc.ReadTagV('rec_data', 0, len(data))
rec_data = numpy.asarray(rec_data)
rec_d = slab.Sound(rec_data)
print('   Recording finished')

rec_d.play()
rec_d.waveform()
"""
