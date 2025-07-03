from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.sound_composer import SoundComposer

my_server, lic_context = connect_to_or_start_server(use_license_context=True)

sound_composer_project = SoundComposer(
    project_path="C:/Users/Public/Documents/Ansys/Acoustics/SAS/Internal-work/pyansys sound - sound composer project for example/SoundComposer-WhatIfScenario-Motor-Gear-HVAC-Noise (SMA modifications).scn"
)
print(sound_composer_project)

sound_composer_project.save(project_path="My_Saved_SoundComposer_Project.scn")
