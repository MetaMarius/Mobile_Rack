import tdt
from win32com.client import Dispatch
import slab
import numpy
import time

proc = Dispatch('RPco.X')


def initialize():
    if proc.ConnectRP2('USB', 1) == 1:
        print('   USB connection to RP2 established')
    elif proc.ConnectRP2('USB', 1) == 0:
        print('   ERROR: USB connection to RP2 failed')
    if proc.ClearCOF() == 1:
        print('   COF cleared')
    elif proc.ClearCOF() == 0:
        print('   ERROR: Failed to clear COF')
    if proc.LoadCOF('C:/Users/neurobio/Desktop/mobile_rack.rcx') == 1:
        print('   rcx file loaded successfully')
    elif proc.LoadCOF('C:/Users/neurobio/Desktop/mobile_rack.rcx') == 0:
        print('   ERROR: Failed to load rcx file ')
    if proc.Run() == 1:
        print('\n   Processor running...')
    elif proc.Run() == 0:
        print('\n   ERROR: Failed to run processor')

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
