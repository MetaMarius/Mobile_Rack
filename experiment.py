from mobile_rack import initialize, get_recording, experiment, create_and_store_file, equalize_loudness, get_drr_recording
import slab

initialize()
recording = get_recording(speaker=0)
recording.waveform()
recording.play()
levels = equalize_loudness(goal_luf=-55, sound_type='pinknoise', rec_channel='dual')

levels = [85.0, 90.0, 91.5, 94.5, 95.5]

# experiment run
experiment_results = experiment(n_reps=1, duration=0.25, sound_type='tone', uso_number=12, levels=levels, room='test',
                                parent_folder='test_parent_folder', subject_folder='test_subject_folder', subject_id='test_id',
                                speaker_distances={
                                    'speaker_1': 150,
                                    'speaker_2': 200,
                                    'speaker_3': 275,
                                    'speaker_4': 400,
                                    'speaker_5': 900
                                }
                                )


speaker_1 = get_recording(speaker=0, distance=0, sound_duration=0.25, level=90, rec_duration=0.25,
                          sound_type='USO', uso_number=29)
speaker_2 = get_recording(speaker=11, distance=5.0, sound_duration=0.25, rec_duration=0.25, level=92)
speaker_3 = get_recording(speaker=10, distance=10.0, sound_duration=0.25, rec_duration=0.25, level=94)
speaker_4 = get_recording(speaker=0, distance=15.0, sound_duration=0.25, rec_duration=0.25, level=96)
speaker_5 = get_recording(speaker=8, distance=20.0, sound_duration=0.25, rec_duration=0.25, level=98)

# DRR recordings, speaker height 106cm
rec = get_drr_recording(speaker=8, distance=9.0, start_level=80, end_level=100, steps=0.5, rec_duration=0.5)
rec.waveform()





