# SPDX-FileCopyrightText: Copyright (c) 2026 Positronic Robotics Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Positronic embodiment configurations for GR00T N1.6.

This module defines modality configurations for Positronic's end-effector
control robots. All configs use unified 'ee_pose' key for EE state/action.

Variants:
    - POSITRONIC_EE_CONFIG: 7D ee_pose (xyz+quat), absolute actions
    - POSITRONIC_EE_JOINTS_CONFIG: 7D ee_pose + joints, absolute actions
    - POSITRONIC_EE_ROT6D_CONFIG: 9D ee_pose (xyz+rot6d), absolute actions
    - POSITRONIC_EE_ROT6D_REL_CONFIG: 9D ee_pose, relative actions
    - POSITRONIC_EE_ROT6D_JOINTS_CONFIG: 9D ee_pose + joints, absolute actions
    - POSITRONIC_EE_ROT6D_JOINTS_REL_CONFIG: 9D ee_pose + joints, relative actions

Usage:
    python -m gr00t.experiment.launch_finetune \
        --modality_config_path gr00t/configs/data/positronic_ee_rot6d_rel.py \
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


def make_positronic_ee_config(
    include_joints: bool = False,
    use_rot6d: bool = False,
    use_relative: bool = False,
):
    """
    Create a Positronic EE control modality configuration.

    Args:
        include_joints: If True, include joint_position in state modality.
        use_rot6d: If True, use 9D xyz+rot6d format. If False, use 7D xyz+quat.
        use_relative: If True, use RELATIVE action representation (requires use_rot6d=True).

    Returns:
        Dictionary with video, state, action, and language ModalityConfig.
    """
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
    action_format = (
        ActionFormat.DEFAULT
        if use_relative
        else (ActionFormat.XYZ_ROT6D if use_rot6d else ActionFormat.DEFAULT)
    )

    # State keys: always use 'ee_pose' for unified interface
    state_keys = ["ee_pose", "grip"]
    if include_joints:
        state_keys.append("joint_position")

    # Action representation
    ee_rep = ActionRepresentation.RELATIVE if use_relative else ActionRepresentation.ABSOLUTE

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
            delta_indices=list(range(16)),
            modality_keys=["ee_pose", "grip"],
            action_configs=[
                # NON_EEF: treat as raw array, don't apply EE-specific SE(3) transforms
                # See comment above for why this is intentional for relative actions
                ActionConfig(
                    rep=ee_rep,
                    type=ActionType.NON_EEF,
                    format=action_format,
                    state_key="ee_pose",
                ),
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


# Standard 7D xyz+quat configs (absolute actions)
POSITRONIC_EE_CONFIG = make_positronic_ee_config()
POSITRONIC_EE_JOINTS_CONFIG = make_positronic_ee_config(include_joints=True)

# 9D xyz+rot6d configs (supports both absolute and relative actions)
POSITRONIC_EE_ROT6D_CONFIG = make_positronic_ee_config(use_rot6d=True)
POSITRONIC_EE_ROT6D_REL_CONFIG = make_positronic_ee_config(use_rot6d=True, use_relative=True)
POSITRONIC_EE_ROT6D_JOINTS_CONFIG = make_positronic_ee_config(include_joints=True, use_rot6d=True)
POSITRONIC_EE_ROT6D_JOINTS_REL_CONFIG = make_positronic_ee_config(
    include_joints=True, use_rot6d=True, use_relative=True
)
