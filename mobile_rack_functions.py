from win32com.client import Dispatch
import slab
import time
import numpy as np
import pyloudnorm as pyln
from datetime import datetime
proc = Dispatch('RPco.X')
SAMPLERATE = 48828
slab.set_default_samplerate(SAMPLERATE)
TDTError = Exception


def initialize(rcx_file_path):
    if proc.ConnectRP2('USB', 1):
        print('Establishing USB connection to RP2...')
    else:
        raise TDTError('Could not establish USB connection to RP2')
    if proc.ClearCOF():
        print('Clearing COF...')
    else:
        raise TDTError('Failed to clear COF')
    if proc.LoadCOF(rcx_file_path):
        print('Loading rcx file...')
    else:
        raise TDTError('Failed to load rcx file. Check for correct rcx file path')
    if proc.Run():
        print('Initialization finished successfully!')
    else:
        raise TDTError('Failed to run processor')


def select_channel(channel):
    proc.SetTagVal('chan_number', channel)
    proc.SoftTrg(1)
    time.sleep(0.01)
    print('Multiplexer output channel set to ' + str(channel))


def write_onto_play_buffer(data):
    flattened_data = data.flatten()
    proc.SetTagVal('playbuflen', len(flattened_data))
    proc._oleobj_.InvokeTypes(15, 0x0, 1, (3, 0), ((8, 0), (3, 0), (0x2005, 0)), 'play_data', 0, flattened_data)


def play(sound=slab.Sound, level=None):
    if level is not None:
        sound.level = level
    data = sound.ramp()
    flattened_data = data.data.flatten()
    proc.SetTagVal('playbuflen', len(flattened_data))
    proc._oleobj_.InvokeTypes(15, 0x0, 1, (3, 0), ((8, 0), (3, 0), (0x2005, 0)), 'play_data', 0, flattened_data)
    proc.SoftTrg(3)


def get_recording(sound=slab.Sound, channel=int(), speaker_distance=float(), level=80, record_stereo=True):
    # set multiplexer channel
    select_channel(channel)
    sound.level = level
    sound = sound.ramp()

    # write sound onto rp2
    write_onto_play_buffer(data=sound.data)

    # set up recording
    proc.SetTagVal('analog_in_1', 1)
    proc.SetTagVal('analog_in_2', 2)
    proc.SetTagVal('recbuflen', len(sound))
    delay = speaker_distance/343.2
    proc.SetTagVal('rec_delay', int(delay*1000))

    # start playback and recording
    proc.SoftTrg(2)
    time.sleep(delay)
    print('recording...')

    # save recording
    time.sleep(sound.duration + 0.1)
    if record_stereo is True:
        rec_data_1 = proc.ReadTagV('rec_data_1', 0, len(sound))
        rec_data_1 = np.asarray(rec_data_1)
        rec_data_2 = proc.ReadTagV('rec_data_2', 0, len(sound))
        rec_data_2 = np.asarray(rec_data_2)
        rec_binaural = slab.Binaural([rec_data_1, rec_data_2])
        print('Recording finished!')
        return rec_binaural
    elif record_stereo is False:
        rec_data_1 = proc.ReadTagV('rec_data_1', 0, len(sound))
        rec_data_1 = np.asarray(rec_data_1)
        rec_monaural = slab.Sound(rec_data_1)
        print('Recording finished!')
        return rec_monaural


def equalize_loudness(sound, channel_distances=dict(), start_level=80, steps=0.25, goal_luf=-25, record_stereo=True,
                      channels_sorted_by_distance=False):
    channel_levels = dict()
    meter = pyln.Meter(SAMPLERATE, block_size=0.200)  # create BS.1770 meter
    for channel in channel_distances:
        recording = get_recording(channel=channel, sound=sound, speaker_distance=channel_distances[channel],
                                  level=start_level, record_stereo=record_stereo)
        current_luf = meter.integrated_loudness(recording.data)  # measure loudness
        level = start_level
        print('Current LUF: ' + str(current_luf) + '   Current Level: ' + str(level))
        while current_luf < goal_luf:
            level += steps
            recording = get_recording(channel=channel, sound=sound, speaker_distance=channel_distances[channel],
                                      level=level, record_stereo=record_stereo)
            current_luf = meter.integrated_loudness(recording.data)  # measure loudness
            print('Current LUF: ' + str(current_luf) + '   Current Level: ' + str(level))
        else:
            channel_levels[channel] = level
            if channels_sorted_by_distance is True:
                start_level = level - 2
    return channel_levels


def experiment(sound, location, sound_type, result_folder_path, subject_id, channel_distances=dict(), levels=dict(),
               playing_order='random_permutation', n_reps=10):
    # create trialsequence
    sound = sound.ramp()
    channels = [channel for channel in channel_distances]
    seq = slab.Trialsequence(conditions=channels, n_reps=n_reps, kind=playing_order)

    # create loop and loop through trialsequence
    n = 1
    response = 0
    right_response = 0
    for channel in seq:
        # adjust level according to speaker
        level = levels[channel]
        sound.level = level

        # write sound onto rp2
        write_onto_play_buffer(data=sound.data)

        # save channel variable in result data
        seq.add_response(channel)

        # set multiplexer channel
        select_channel(channel=channel)

        # trigger playback
        proc.SoftTrg(3)

        # wait for response
        while proc.GetTagVal('response') == 0:
            time.sleep(0.001)

        # save given response to result data
        if proc.GetTagVal('response') == 1.0:
            response = 0
        elif proc.GetTagVal('response') == 2.0:
            response = 1
        elif proc.GetTagVal('response') == 4.0:
            response = 2
        elif proc.GetTagVal('response') == 8.0:
            response = 3
        elif proc.GetTagVal('response') == 16.0:
            response = 4
        seq.add_response(response)

        # save if response was correct or not to result data
        if response == channel:
            seq.add_response(1)
            right_response += 1
        else:
            seq.add_response(0)
        seq.add_response(level)
        # print out live result
        print(str(right_response) + ' / ' + str(n))
        n += 1
        time.sleep(0.5)
    result_file = slab.ResultsFile(subject=subject_id, folder=result_folder_path)
    result_file.write(subject_id, tag='subject_ID')
    today = datetime.now()
    result_file.write(today.strftime('%Y/%m/%d'), tag='Date')
    result_file.write(today.strftime('%H:%M:%S'), tag='Time')
    result_file.write(location, tag='location')
    result_file.write(sound_type, tag='sound_type')
    result_file.write(channel_distances, tag='channel_distances')
    result_file.write(levels, tag='channel_levels')
    result_file.write(seq, tag='trialsequence')
    print("Finished")
    return result_file




