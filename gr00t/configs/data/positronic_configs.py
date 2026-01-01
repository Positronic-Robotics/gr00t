# SPDX-FileCopyrightText: Copyright (c) 2026 Positronic Robotics Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Positronic embodiment configurations for GR00T N1.6.

This module defines modality configurations for Positronic's end-effector
control robots. The configs support absolute EE position control with
optional joint position feedback.

Usage:
    python -m gr00t.experiment.launch_finetune \
        --modality_config_path gr00t/configs/data/positronic_configs.py \
        --embodiment_tag NEW_EMBODIMENT \
        ...
"""

from gr00t.data.types import (
    ActionConfig,
    ActionFormat,
    ActionRepresentation,
    ActionType,
    ModalityConfig,
)


def make_positronic_ee_config(include_joints: bool = False):
    """
    Create a Positronic EE control modality configuration.

    Args:
        include_joints: If True, include joint_position in state modality
                       for joint feedback during EE control.

    Returns:
        Dictionary with video, state, action, and language ModalityConfig.
    """
    state_keys = [
        "robot_position_translation",  # 3 dims: x, y, z
        "robot_position_quaternion",  # 4 dims: qw, qx, qy, qz
        "grip",  # 1 dim: gripper state
    ]
    if include_joints:
        state_keys.append("joint_position")  # 7 dims for 7-DOF arm

    return {
        "video": ModalityConfig(
            delta_indices=[0],
            modality_keys=["exterior_image_1", "wrist_image"],
        ),
        "state": ModalityConfig(
            delta_indices=[0],
            modality_keys=state_keys,
        ),
        "action": ModalityConfig(
            delta_indices=list(range(16)),  # 16-step action horizon
            modality_keys=[
                "target_robot_position_translation",  # 3 dims
                "target_robot_position_quaternion",  # 4 dims
                "target_grip",  # 1 dim
            ],
            action_configs=[
                # Translation: absolute EE position
                ActionConfig(
                    rep=ActionRepresentation.ABSOLUTE,
                    type=ActionType.EEF,
                    format=ActionFormat.DEFAULT,
                ),
                # Rotation: absolute quaternion
                ActionConfig(
                    rep=ActionRepresentation.ABSOLUTE,
                    type=ActionType.EEF,
                    format=ActionFormat.DEFAULT,
                ),
                # Gripper: absolute position
                ActionConfig(
                    rep=ActionRepresentation.ABSOLUTE,
                    type=ActionType.NON_EEF,
                    format=ActionFormat.DEFAULT,
                ),
            ],
        ),
        "language": ModalityConfig(
            delta_indices=[0],
            modality_keys=["annotation.language.language_instruction"],
        ),
    }


# Create the configurations (registration done by wrapper files)
POSITRONIC_EE_CONFIG = make_positronic_ee_config(include_joints=False)
POSITRONIC_EE_JOINTS_CONFIG = make_positronic_ee_config(include_joints=True)
