"""DROID checkpoint contracts survive fine-tuning configuration.

Fixtures are from nvidia/GR00T-N1.7-DROID revision 05e7cc9 on Hugging Face.
"""

import json
from pathlib import Path

from gr00t.configs.finetune_config import FinetuneConfig
from gr00t.data.types import ActionFormat, ActionRepresentation, ActionType
from gr00t.experiment.launch_finetune import build_config
import pytest


CHECKPOINT = Path(__file__).parents[2] / "fixtures" / "droid"
EMBODIMENT = "oxe_droid_relative_eef_relative_joint"


@pytest.mark.parametrize(
    "cameras", [None, ["exterior_image_1_left", "exterior_image_2_left", "wrist_image_left"]]
)
def test_finetuning_retains_droid_checkpoint_contract(cameras):
    config = build_config(
        FinetuneConfig(
            base_model_path=str(CHECKPOINT),
            dataset_path="/dataset",
            embodiment_tag=EMBODIMENT,
            video_keys=cameras,
            resume_from_checkpoint=True,
        )
    )
    saved = json.loads((CHECKPOINT / "processor_config.json").read_text())["processor_kwargs"]
    modalities = config.data.modality_configs[EMBODIMENT]
    assert modalities["video"].delta_indices == [0]
    assert modalities["video"].modality_keys == (
        cameras or saved["modality_configs"][EMBODIMENT]["video"]["modality_keys"]
    )
    assert modalities["state"].delta_indices == [0]
    assert modalities["action"].delta_indices == list(range(40))
    eef, grip, joints = modalities["action"].action_configs
    assert (eef.rep, eef.type, eef.format) == (
        ActionRepresentation.RELATIVE,
        ActionType.EEF,
        ActionFormat.XYZ_ROT6D,
    )
    assert grip.rep is ActionRepresentation.ABSOLUTE
    assert joints.rep is ActionRepresentation.RELATIVE
    assert config.model.use_relative_action
    assert config.model.diffusion_model_cfg["num_layers"] == 32
    assert config.model.select_layer == 16
    assert config.model.action_horizon == 40
    assert config.model.shortest_image_edge == saved["shortest_image_edge"] == 256
    assert config.model.crop_fraction == saved["crop_fraction"] == 0.95
    assert config.model.color_jitter_params == saved["color_jitter_params"]
    assert not config.model.letter_box_transform
    assert not config.model.tune_llm
    assert not config.model.tune_visual
    assert config.training.resume_from_checkpoint


def test_camera_override_does_not_change_a_subsequent_run():
    arguments = dict(
        base_model_path=str(CHECKPOINT), dataset_path="/dataset", embodiment_tag=EMBODIMENT
    )
    build_config(FinetuneConfig(**arguments, video_keys=["custom_wrist", "custom_external"]))
    config = build_config(FinetuneConfig(**arguments))
    assert config.data.modality_configs[EMBODIMENT]["video"].modality_keys == [
        "exterior_image_1_left",
        "wrist_image_left",
    ]
