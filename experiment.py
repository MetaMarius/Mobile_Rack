from mobile_rack import initialize, get_recording, experiment, create_and_store_file, equalize_loudness, get_drr_recording
import slab

initialize()

levels = equalize_loudness(goal_luf=-55, sound_type='pinknoise', rec_channel='dual')

speaker_setup = {
    'speaker_1': 200,
    'speaker_2': 0,
    'speaker_3': 0,
    'speaker_4': 0,
    'speaker_5': 0
}

# experiment run
experiment = experiment(n_reps=3, duration=0.25, sound_type='USOrand', levels=levels)

# get results and store them
experiment_results = create_and_store_file(parent_folder='first_tries', subject_folder='Marius', subject_id='Marius',
                                          trialsequence=experiment, speaker_setup=speaker_setup)


speaker_1 = get_recording(speaker=2, distance=0, sound_duration=0.25, level=90, rec_duration=0.25,
                          sound_type='USO', uso_number=29)
speaker_2 = get_recording(speaker=11, distance=5.0, sound_duration=0.25, rec_duration=0.25, level=92)
speaker_3 = get_recording(speaker=10, distance=10.0, sound_duration=0.25, rec_duration=0.25, level=94)
speaker_4 = get_recording(speaker=0, distance=15.0, sound_duration=0.25, rec_duration=0.25, level=96)
speaker_5 = get_recording(speaker=8, distance=20.0, sound_duration=0.25, rec_duration=0.25, level=98)

# DRR recordings, speaker height 106cm
rec = get_drr_recording(speaker=8, distance=3.4, start_level=80, end_level=100, steps=0.5, rec_duration=0.5)
rec.waveform()




look = slab.Binaural('data/drr_recordings/FFhallway/uso/FFhallway_uso_distance-1015_level-88.wav')
look.waveform()


slab.Binaural('data/drr_recordings/FFhallway/chirp/FFhallway_chirp_distance-1015_level-80.wav').waveform()
slab.Binaural('data/drr_recordings/FFhallway/chirp/FFhallway_chirp_distance-1015_level-100.wav').waveform()

slab.Binaural('data/drr_recordings/FFhallway/chirp/N_FFhallway_chirp_distance-1015_level-80.wav').waveform()
slab.Binaural('data/drr_recordings/FFhallway/chirp/N_FFhallway_chirp_distance-1015_level-100.wav').waveform()
