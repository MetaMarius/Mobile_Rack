import random
from mobile_rack_functions import initialize, select_speaker, select_channel, play, record_slider_val, get_slider_val, map_from_to
import slab
import numpy as np
import time

SAMPLERATE = 48848
slab.set_default_samplerate(SAMPLERATE)
initialize(rcx_file_path='C:/Users/neurobio/Desktop/mobile_rack.rcx')

slider_max = get_slider_val(prompt="Move slider to maximum point. Press enter when ready!")
slider_min = get_slider_val(prompt="Move slider to minimum point. Press enter when ready!")

channel = int(map_from_to(get_slider_val(), slider_min, slider_max, 0, 4))

key_codes = (range(1, 5))
test_sound = slab.Sound('data/uso_300ms/uso_300ms_2.wav')
pink = slab.Sound.pinknoise(duration=0.5)

subject_ID = 'sub_12'
file = slab.ResultsFile(subject=subject_ID)
file.write(subject_ID)

uso_ids = range(1, 30)
conditions = [1, 2, 3, 4]
trials = slab.Trialsequence(conditions=conditions, n_reps=5)
# distances = {1: 8.0, 2: 9.0, 3: 10.0, 4: 11.0, 5: 12.0}
# distances = {1: 6.0, 2: 6.5, 3: 7.0, 4: 7.5, 5: 8.0}
# distances = {1: 4.0, 2: 4.5, 3: 5.0, 4: 5.5, 5: 6.0}
distances = {1: 2.0, 2: 2.5, 3: 3.0, 4: 3.5, 5: 4.0}
# normalised for -60dB LUFS
levels_per_distance = {
    '12.0': 97.75,
    '11.0': 97.75,
    '10.0': 98.5,
    '9.0': 98,
    '8.0': 97,
    '7.5': 97.5,
    '7.0': 96,
    '6.5': 96.5,
    '6.0': 96.25,
    '5.5': 95.5,
    '5.0': 94.75,
    '4.5': 94.5,
    '4.0': 94.25,
    '3.5': 93.5,
    '3.0': 92.75,
    '2.5': 91.25,
    '2.0': 90,
    '1.5': 88,
    '1.0': 85.75,
}
# levels = {0: 92, 4: 93.0}
file.write(distances, tag='distances')
target_speaker = 5

for distractor_speaker in trials:
    # curr_conditions = [1, 2, 3, 4, 5]
    # curr_conditions.remove(distractor_speaker)
    # target_speaker = random.choice(curr_conditions)
    speakers = [target_speaker, distractor_speaker]
    order = np.random.permutation(len(speakers))
    uso_id = np.random.choice(uso_ids)
    sound = slab.Sound(f'data/uso_300ms/uso_300ms_{uso_id}.wav')
    for idx in order:
        speaker = speakers[idx]
        select_speaker(speaker)
        level = levels_per_distance[str(distances[speaker])]
        play(sound=sound, level=level)
        time.sleep(1)
    # response = input()
    response = get_slider_val()
    print(response)
    # wait_for_button_press()
    # response = get_button_press() - 2
    response = int(response)
    # print(response)
    # interval = np.where(order == 0)[0][0]
    # print('interval', interval)
    # interval_key = key_codes[interval]
    # response = response == interval_key
    distance_1 = distances[speakers[order[0]]]
    distance_2 = distances[speakers[order[1]]]
    correct = False
    if response == 1 and distance_1 < distance_2:
        correct = True
    elif response == 2 and distance_1 > distance_2:
        correct = True
    print('Response:', response, 'Correct:', correct)
    trials.add_response({
        'distance_1': distance_1,
        'distance_2': distance_2,
        'response': response,
        'correct': correct,
        'stim': f'uso_300ms_{uso_id}.wav'
    })
    trials.print_trial_info()
    # time.sleep(0.3)
file.write(trials)