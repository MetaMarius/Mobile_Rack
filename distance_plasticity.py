from mobile_rack_functions import initialize, select_speaker, select_channel, play, record_slider_val, get_slider_val, map_from_to
import slab
import time
import random
from os import listdir
import json

###############

subject_ID = 'jakab'

###############

SAMPLERATE = 48848
slab.set_default_samplerate(SAMPLERATE)
initialize(rcx_file_path='C:/Users/neurobio/Desktop/mobile_rack.rcx')
channels = [0, 1, 2, 3, 4]
USO_folder = 'data/uso_300ms/'
USO_file_names = listdir(USO_folder)
USOs = slab.Precomputed([slab.Sound(f'{USO_folder}{f}') for f in USO_file_names])
slider_vals = {i: float() for i in range(5)}
with open('config.json') as file:
    cfg = json.load(file)
chan_to_dist = cfg["chan_to_dist"]
dist_to_level = cfg["dist_to_level"]

################

# Calibrate slider

slider_vals[0] = record_slider_val()
slider_vals[1] = record_slider_val()
slider_vals[2] = record_slider_val()
slider_vals[3] = record_slider_val()
slider_vals[4] = record_slider_val()

################

# Visual mapping


def visual_mapping():
    file = slab.ResultsFile(subject=subject_ID)
    file.write("visual_mapping", tag="stage")
    file.write(slider_vals, tag="slider_vals")
    trial_num = 0
    while True:
        trial_num += 1
        absolute_distance = input("Enter distance (or 'q' to quit task):")
        if absolute_distance == "q":
            break
        print(f"Trial: {trial_num}")
        absolute_distance = float(absolute_distance)
        file.write(absolute_distance, tag="solution")
        response = record_slider_val()
        print("Response:", response)
        file.write(response, tag="response")
    print("Done with visual mapping task")

################

# Sound source distance mapping task (naive test)


def sound_mapping():
    file = slab.ResultsFile(subject=subject_ID)
    file.write("sound_mapping", tag="stage")
    file.write(slider_vals, tag="slider_vals")
    sound = random.choice(USOs)
    seq = slab.Trialsequence(conditions=channels, n_reps=2)
    for channel in seq:
        spk_dist = chan_to_dist[str(channel)]
        select_channel(channel)
        t_before = time.time()
        play(sound=sound, level=dist_to_level[str(spk_dist)])
        time.sleep(sound.duration)
        file.write(channel, tag="channel")
        file.write(spk_dist, tag="spk_dist")
        slider_val = record_slider_val()
        t_after = time.time()
        response_time = t_after - t_before
        file.write(slider_val, tag="slider_val")
        file.write(response_time, tag="response_time")
    print("Done with sound mapping task")

################

# Training


def training():
    file = slab.ResultsFile(subject=subject_ID)
    file.write("training", tag="stage")
    file.write(slider_vals, tag="slider_vals")
    sound = random.choice(USOs)
    isi = 1.0  # in seconds
    training_duration = 180.0  # in seconds
    file.write(isi, tag="isi")
    file.write(training_duration, tag="training_duration")
    seq = slab.Trialsequence(conditions=int(training_duration / isi))
    file.write(seq, tag="seq")
    for trial in seq:
        channel = int(map_from_to(get_slider_val(), slider_vals[0], slider_vals[max(slider_vals.keys())], min(channels), max(channels)))
        spk_dist = chan_to_dist[str(channel)]
        select_channel(channel)
        print(f"Playing trial: {seq.this_n + 1}/{seq.n_trials}")
        play(sound=sound, level=dist_to_level[str(spk_dist)])
        time.sleep(isi)
        file.write(spk_dist, tag="spk_dist")
    print("Done with training")

################

# Distance discrimination task


def distance_discrimination_task():
    file = slab.ResultsFile(subject=subject_ID)
    file.write("test_distance_discrimination", tag="stage")
    file.write(slider_vals, tag="slider_vals")
    sound = random.choice(USOs)
    seq = slab.Trialsequence(conditions=channels, n_reps=10)
    file.write(seq, tag="seq")
    for channel in seq:
        spk_dist = chan_to_dist[str(channel)]
        select_channel(channel)
        t_before = time.time()
        play(sound=sound, level=dist_to_level[str(spk_dist)])
        time.sleep(sound.duration)
        file.write(channel, tag="channel")
        file.write(spk_dist, tag="spk_dist")
        slider_val = record_slider_val()
        t_after = time.time()
        response_time = t_after - t_before
        file.write(slider_val, tag="slider_val")
        file.write(response_time, tag="response_time")
    print("Done with distance discrimination task")
