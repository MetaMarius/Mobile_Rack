from mobile_rack import initialize, get_recording, experiment, create_and_store_file, equalize_loudness
import slab
from datetime import datetime
initialize()

levels = equalize_loudness(goal_luf=-55, sound_type='USO')

# experiment run
first_run = experiment(speaker=[0, 2, 8, 10, 11], n_reps=3, levels=levels, duration=0.25, sound_type='USO')

# get results and store them
first_run_results = create_and_store_file(parent_folder='first_tries', subject_folder='Marius', subject_id='Marius', trialsequence=first_run)
first_run_results.read()


speaker_1 = get_recording(speaker=2, distance=0, duration=0.25, level=90)
speaker_2 = get_recording(speaker=11, distance=5.0, duration=0.25, level=92)
speaker_3 = get_recording(speaker=10, distance=10.0, duration=0.25, level=94)
speaker_4 = get_recording(speaker=0, distance=15.0, duration=0.25, level=96)
speaker_5 = get_recording(speaker=8, distance=20.0, duration=0.25, level=98)