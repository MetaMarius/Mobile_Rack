
from win32com.client import Dispatch 
import slab
import numpy
import time
from datetime import datetime
import pyloudnorm as pyln
import os
import pathlib

pathlib.Path(os.getcwd())
cwd = pathlib.Path(os.getcwd())
filepath = cwd / 'data' / 'uso_300ms' / 'uso_300ms_15.wav'

proc = Dispatch('RPco.X')
SAMPLERATE = 48828
slab.set_default_samplerate(SAMPLERATE)


def initialize():
    if proc.ConnectRP2('USB', 1):
        print('   USB connection to RP2 established')
    else:
        print('   ERROR: USB connection to RP2 failed')
    if proc.ClearCOF():
        print('   COF cleared')
    else:
        print('   ERROR: Failed to clear COF')
    if proc.LoadCOF('C:/Users/neurobio/Desktop/mobile_rack.rcx'):
        print('   rcx file loaded successfully')
    else:
        print('   ERROR: Failed to load rcx file ')
    if proc.Run():
        print('\n   Processor running...')
    else:
        print('\n   ERROR: Failed to run processor')


def get_recording(speaker, distance, tone_frequency=800, duration=1.0, level=80, rec_channel=1, sound_type='pinknoise'):
    # set multiplexer channel
    proc.SetTagVal('chan_number', speaker)
    proc.SoftTrg(1)
    time.sleep(0.1)
    print('\n   Multiplexer output channel set to ' + str(speaker))

    # create sound
    if sound_type == 'tone':
        sound = slab.Sound.tone(frequency=tone_frequency, duration=duration, level=level)
    elif sound_type == 'pinknoise':
        sound = slab.Sound.pinknoise(duration=duration, level=level)
    elif sound_type == 'chirp':
        sound = slab.Sound.chirp(duration=duration, level=level)
    elif sound_type == 'USO':
        sound = slab.Sound(filepath)
        sound.level = level
    sound = sound.ramp(duration=0.05)


    # write sound onto rp2
    data = sound.data.flatten()
    proc.SetTagVal('playbuflen', len(data))
    proc._oleobj_.InvokeTypes(15, 0x0, 1, (3, 0), ((8, 0), (3, 0), (0x2005, 0)), 'play_data', 0, data)

    # set up recording
    proc.SetTagVal('analog_in', rec_channel)
    proc.SetTagVal('recbuflen', len(data))
    delay = distance/343.2
    proc.SetTagVal('rec_delay', int(delay*1000))

    # start playback and recording
    proc.SoftTrg(2)
    time.sleep(delay)
    print('recording...')

    # save recording
    time.sleep(duration + 0.1)
    rec_data = proc.ReadTagV('rec_data', 0, len(data))
    rec_data = numpy.asarray(rec_data)
    rec_binaural = slab.Binaural(rec_data)
    print('   Recording finished')
    return rec_binaural


def equalize_loudness(goal_luf=-25, dis_sp_1=1, dis_sp_2=1.5, dis_sp_3=3, dis_sp_4=6, dis_sp_5=10,
                      speakers=[2, 11, 10, 0, 8], level=80, sound_type='pinknoise'):
    level_list = []
    meter = pyln.Meter(SAMPLERATE, block_size=0.200)  # create BS.1770 meter
    for speaker in speakers:
        if speaker == 2:
            dis = dis_sp_1
        elif speaker == 11:
            dis = dis_sp_2
        elif speaker == 10:
            dis = dis_sp_3
        elif speaker == 0:
            dis = dis_sp_4
        elif speaker == 8:
            dis = dis_sp_5
        recording = get_recording(speaker=speaker, distance=dis, duration=0.25, level=level, sound_type=sound_type)
        current_luf = meter.integrated_loudness(recording.data)  # measure loudness
        while current_luf < goal_luf:
            level += 0.5
            recording = get_recording(speaker=speaker, distance=dis, duration=0.25, level=level, sound_type=sound_type)
            current_luf = meter.integrated_loudness(recording.data)  # measure loudness
            print('Current LUF: ' + str(current_luf) + '   Current Level: ' + str(level))
        else:
            level_list.append(level)
            level -= 3

    return level_list


def experiment(speaker=[2, 11, 10, 0, 8], n_reps=10, playing_order='random_permutation', tone_frequency=800,
               duration=1.0, levels=[], sound_type='pinknoise'):
    # create trialsequence
    seq = slab.Trialsequence(conditions=speaker, n_reps=n_reps, kind=playing_order)

    # create loop and loop through trialsequence
    n = 1
    response = 0
    right_response = 0
    for speaker in seq:
        # adjust level according to speaker
        if speaker == 2:
            level = levels[0]
        elif speaker == 11:
            level = levels[1]
        elif speaker == 10:
            level = levels[2]
        elif speaker == 0:
            level = levels[3]
        elif speaker == 8:
            level = levels[4]

        # create sound
        if sound_type == 'tone':
            test_sound = slab.Sound.tone(frequency=tone_frequency, duration=duration, level=level)
        elif sound_type == 'pinknoise':
            test_sound = slab.Sound.pinknoise(duration=duration, level=level)
        elif sound_type == 'chirp':
            test_sound = slab.Sound.chirp(duration=duration, level=level)
        elif sound_type == 'USO':
            test_sound = slab.Sound(filepath)
            test_sound.level = level
        test_sound = test_sound.ramp(duration=0.05)

        # write sound onto rp2
        data = test_sound.data.flatten()
        proc.SetTagVal('playbuflen', len(data))
        proc._oleobj_.InvokeTypes(15, 0x0, 1, (3, 0), ((8, 0), (3, 0), (0x2005, 0)), 'play_data', 0, data)

        # save speaker variable in result data
        seq.add_response(speaker)

        # set multiplexer channel according to speaker
        proc.SetTagVal('chan_number', speaker)
        proc.SoftTrg(1)
        time.sleep(0.5)

        # trigger playback
        proc.SoftTrg(3)

        # wait for response
        while proc.GetTagVal('response') == 0:
            time.sleep(0.001)

        # save given response to result data
        if proc.GetTagVal('response') == 1.0:
            response = 1
        elif proc.GetTagVal('response') == 2.0:
            response = 2
        elif proc.GetTagVal('response') == 4.0:
            response = 3
        elif proc.GetTagVal('response') == 8.0:
            response = 4
        elif proc.GetTagVal('response') == 16.0:
            response = 5
        seq.add_response(response)

        # save if response was correct or not to result data
        if response == 1 and speaker == 2:
            seq.add_response(1)
            right_response += 1
        elif response == 2 and speaker == 11:
            seq.add_response(1)
            right_response += 1
        elif response == 3 and speaker == 10:
            seq.add_response(1)
            right_response += 1
        elif response == 4 and speaker == 0:
            seq.add_response(1)
            right_response += 1
        elif response == 5 and speaker == 8:
            seq.add_response(1)
            right_response += 1
        else:
            seq.add_response(0)

        # print out live result
        print(str(right_response) + ' / ' + str(n))
        n += 1
    responses = seq.save_json("sequence.json", clobber=True)
    print("Finished")
    return seq


def create_and_store_file(parent_folder, subject_folder, subject_id, trialsequence):
    file = slab.ResultsFile(subject=subject_folder, folder=parent_folder)
    subject_id = subject_id
    file.write(subject_id, tag='subject_ID')
    today = datetime.now()
    file.write(today.strftime('%Y/%m/%d'), tag='Date')
    file.write(today.strftime('%H:%M:%S'), tag='Time')
    file.write(trialsequence, tag='Trial')
    return file




