docker build -t mne_bpy:latest -f Dockerfile . 
singularity build --force mne_bpy.sif docker-daemon://mne_bpy:latest 