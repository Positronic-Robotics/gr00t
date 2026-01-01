# Positronic EE config (without joint feedback)
from gr00t.configs.data.embodiment_configs import register_modality_config
from gr00t.configs.data.positronic_configs import POSITRONIC_EE_CONFIG
from gr00t.data.embodiment_tags import EmbodimentTag

register_modality_config(POSITRONIC_EE_CONFIG, embodiment_tag=EmbodimentTag.NEW_EMBODIMENT)
