# SPDX-FileCopyrightText: Copyright (c) 2026 Positronic Robotics Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Positronic embodiment configurations for GR00T N1.6.

Two action spaces:
    EE (end-effector): action key is 'ee_pose' (7D quat or 9D rot6d)
    Joints: action key is 'joint_position' (7D joint positions)

EE variants:
    - POSITRONIC_EE_CONFIG: 7D ee_pose, absolute
    - POSITRONIC_EE_JOINTS_CONFIG: 7D ee_pose + joint obs, absolute
    - POSITRONIC_EE_ROT6D_CONFIG: 9D ee_pose, absolute
    - POSITRONIC_EE_ROT6D_REL_CONFIG: 9D ee_pose, relative
    - POSITRONIC_EE_ROT6D_JOINTS_CONFIG: 9D ee_pose + joint obs, absolute
    - POSITRONIC_EE_ROT6D_JOINTS_REL_CONFIG: 9D ee_pose + joint obs, relative

Joint variants:
    - POSITRONIC_JOINTS_CONFIG: joint_position actions + joint/ee obs

Usage:
    python -m gr00t.experiment.launch_finetune \\
        --modality_config_path gr00t/configs/data/positronic_ee_rot6d_rel.py \\
        --embodiment_tag NEW_EMBODIMENT \\
        ...
"""

from gr00t.data.types import (
    ActionConfig,
    ActionFormat,
    ActionRepresentation,
    ActionType,
    ModalityConfig,
)


# All configs share this video/language structure
_VIDEO = ModalityConfig(delta_indices=[0], modality_keys=["exterior_image_1", "wrist_image"])
_LANGUAGE = ModalityConfig(
    delta_indices=[0], modality_keys=["annotation.language.language_instruction"]
)

# IMPORTANT: ActionType and ActionFormat selection for relative actions
#
# For RELATIVE actions, we use NON_EEF + DEFAULT intentionally:
#   - Positronic computes relative actions in its own data pipeline using proper
#     SE(3) math (rotation composition, not element-wise subtraction)
#   - The pre-computed relative values are fed to GR00T as action data
#   - NON_EEF + DEFAULT ensures GR00T treats these as raw arrays without
#     applying additional SE(3) transformations
#
# DO NOT "fix" this to EEF + XYZ_ROT6D for relative actions:
#   - That would make GR00T interpret already-relative values as absolute EE poses
#   - GR00T would then apply its own relative conversion (double transformation)
#   - Result: incorrect rotation deltas and training failure
#
# For ABSOLUTE actions, format selection is less critical since no relative
# conversion happens, but we use XYZ_ROT6D for rot6d to match the data format.

_GRIP_ACTION = ActionConfig(
    rep=ActionRepresentation.ABSOLUTE,
    type=ActionType.NON_EEF,
    format=ActionFormat.DEFAULT,
)


def _make_action_config(action_key, rep, fmt):
    return ModalityConfig(
        delta_indices=list(range(16)),
        modality_keys=[action_key, "grip"],
        action_configs=[
            ActionConfig(rep=rep, type=ActionType.NON_EEF, format=fmt, state_key=action_key),
            _GRIP_ACTION,
        ],
    )


def make_positronic_ee_config(include_joints=False, use_rot6d=False, use_relative=False):
    """EE action space config. Action key is 'ee_pose'."""
    action_rep = ActionRepresentation.RELATIVE if use_relative else ActionRepresentation.ABSOLUTE
    action_fmt = (
        ActionFormat.DEFAULT
        if use_relative
        else (ActionFormat.XYZ_ROT6D if use_rot6d else ActionFormat.DEFAULT)
    )

    state_keys = ["ee_pose", "grip"]
    if include_joints:
        state_keys.append("joint_position")

    return {
        "video": _VIDEO,
        "state": ModalityConfig(delta_indices=[0], modality_keys=state_keys),
        "action": _make_action_config("ee_pose", action_rep, action_fmt),
        "language": _LANGUAGE,
    }


def make_positronic_joints_config():
    """Joint action space config. Action key is 'joint_position'."""
    return {
        "video": _VIDEO,
        "state": ModalityConfig(
            delta_indices=[0], modality_keys=["ee_pose", "grip", "joint_position"]
        ),
        "action": _make_action_config(
            "joint_position", ActionRepresentation.ABSOLUTE, ActionFormat.DEFAULT
        ),
        "language": _LANGUAGE,
    }


POSITRONIC_EE_CONFIG = make_positronic_ee_config()
POSITRONIC_EE_JOINTS_CONFIG = make_positronic_ee_config(include_joints=True)

POSITRONIC_EE_ROT6D_CONFIG = make_positronic_ee_config(use_rot6d=True)
POSITRONIC_EE_ROT6D_REL_CONFIG = make_positronic_ee_config(use_rot6d=True, use_relative=True)
POSITRONIC_EE_ROT6D_JOINTS_CONFIG = make_positronic_ee_config(include_joints=True, use_rot6d=True)
POSITRONIC_EE_ROT6D_JOINTS_REL_CONFIG = make_positronic_ee_config(
    include_joints=True, use_rot6d=True, use_relative=True
)

POSITRONIC_JOINTS_CONFIG = make_positronic_joints_config()
