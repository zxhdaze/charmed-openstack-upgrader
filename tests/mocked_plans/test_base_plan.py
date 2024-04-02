#  Copyright 2023 Canonical Limited
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""Test all sample plans."""
from unittest.mock import patch

import pytest
import logging

from cou.commands import CLIargs
from cou.steps.analyze import Analysis
from cou.steps.plan import generate_plan


@pytest.mark.asyncio
@patch("cou.utils.nova_compute.get_instance_count", return_value=0)
async def test_base_plan(_, sample_plans):
    """Testing all sample plans."""
    args = CLIargs("plan", auto_approve=True)
    model, exp_plan = sample_plans["base.yaml"]

    analysis_results = await Analysis.create(model)
    plan = await generate_plan(analysis_results, args)

    assert str(plan) == exp_plan


@pytest.mark.asyncio
@patch("cou.utils.nova_compute.get_instance_count", side_effect=[1, 0, 1])
async def test_base_plan_non_empty(_, sample_plans, caplog):
    """Testing non-empty hypervisor logs."""
    args = CLIargs("plan", auto_approve=True)
    model, __ = sample_plans["base.yaml"]

    with caplog.at_level(logging.INFO):
        analysis_results = await Analysis.create(model)
        await generate_plan(analysis_results, args)

    expected_log = (
        'Skipped (non-empty) hypervisors: ["Machine(machine_id=\'1\', apps=(\'nova-compute\', '
        '\'ovn-chassis\'), az=\'az-0\')", "Machine(machine_id=\'3\', apps=(\'nova-compute\', '
        '\'ovn-chassis\'), az=\'az-0\')"]'
    )
    assert any(expected_log in message for message in caplog.messages), \
        f"Expected log message not found: '{expected_log}'"
    