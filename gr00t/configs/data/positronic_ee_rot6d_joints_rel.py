# Positronic EE config with 9D xyz+rot6d format and joint feedback (RELATIVE actions)
from gr00t.configs.data.embodiment_configs import register_modality_config
from gr00t.configs.data.positronic_configs import POSITRONIC_EE_ROT6D_JOINTS_REL_CONFIG
from gr00t.data.embodiment_tags import EmbodimentTag

register_modality_config(POSITRONIC_EE_ROT6D_JOINTS_REL_CONFIG, embodiment_tag=EmbodimentTag.NEW_EMBODIMENT)
