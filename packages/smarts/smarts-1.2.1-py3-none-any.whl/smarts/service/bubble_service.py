# MIT License
#
# Copyright (C) 2022. Huawei Technologies Co., Ltd. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from typing import Dict, Optional

from build.lib.smarts.zoo.worker_pb2 import Observation
from smarts.core.agent_interface import AgentInterface
from smarts.core.agent_manager import AgentManager
from smarts.core.bubble_manager import BubbleManager
from smarts.core.controllers import ActionSpaceType
from smarts.core.smarts import SMARTS
from smarts.service import bubble_pb2, bubble_pb2_grpc
from smarts.service.service_base import ServiceBase


class BubbleService(ServiceBase, bubble_pb2_grpc.BubbleServicer):
    def __init__(self) -> None:
        self._smarts = None
        self._last_observations = {}
        super().__init__()

    def setup(self, smarts):
        self._smarts = smarts
        agent_manager: AgentManager = self._smarts.agent_manager
        agent_manager.add_social_agent_observations_callback(
            self._observation_callback, "bubble_service"
        )

    def _observation_callback(self, obs: Dict[str, Observation]):
        self._last_observations = obs

    def ExamineBubbles(self, request: bubble_pb2.BubbleRequest, context):
        bubble_manager: BubbleManager = self._smarts._bubble_manager
        bubbles = bubble_manager.vehicle_ids_per_bubble()

        def make_bi(bb: bubble_manager.Bubble, veh_ids):
            bi = bubble_pb2.BubbleInfo()
            bi.bubble_id = bb.id
            bi.vehicle_ids.extend(veh_ids)
            return bi

        bubble_infos = bubble_pb2.BubbleInfos()
        bubble_infos.bubble_infos[:] = [
            make_bi(bb, veh_ids) for bb, veh_ids in bubbles.items()
        ]
        return bubble_infos

    def GetObservations(self, request: bubble_pb2.ObservationRequest, context):
        agent_obs = bubble_pb2.AgentObservations()
        for id_, ob in self._last_observations:
            # if not id_ in request.agent_ids:
            #     continue
            observation = bubble_pb2.AgentObservation()
            observation.data = ob
            agent_obs.observations[id_] = observation

    def ActOnBubbleAgents(self, request: bubble_pb2.AgentActions, context):
        agent_actions: Dict[str, bubble_pb2.Action] = request.actions
        agent_manager: AgentManager = self._smarts.agent_manager
        for agent_id, action in agent_actions.items():
            action_space_type = ActionSpaceType(action.action_space_type)
            agent_interface: AgentInterface = (
                agent_manager.agent_interface_for_agent_id(agent_id=agent_id)
            )
            agent_manager.reserve_social_agent_action(
                self._smarts, agent_id, action.data
            )

        return bubble_pb2.AgentObservations()
