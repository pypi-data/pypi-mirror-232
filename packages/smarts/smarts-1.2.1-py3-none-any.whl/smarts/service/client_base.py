# MIT License
#
# Copyright (C) 2021. Huawei Technologies Co., Ltd. All rights reserved.
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
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from concurrent.futures import Future
from dataclasses import dataclass
from typing import Dict, Iterable, List

SerializedAction = bytes
AgentID = str


@dataclass
class Session:
    pass


@dataclass
class AgentAction:
    action_: SerializedAction


@dataclass
class AgentFilter:
    bubble_id_filter: List[str]
    regex_filter: str


@dataclass
class AgentObservation:
    payload: bytes


class ClientBase:
    def agent_ids_stream(
        self, agent_filter: AgentFilter, session: Session
    ) -> Iterable[Future]:  # Iterable(Future[List[str]])
        assert NotImplementedError()

    def get_observations_stream(
        self, agent_filter: AgentFilter, session: Session
    ) -> Iterable[Future]:  # Iterable(Future[List[AgentObservation]])
        assert NotImplementedError()

    def instance_info(self):
        assert NotImplementedError()

    def send_actions(self, actions: Dict[AgentID, AgentAction], session: Session):
        assert NotImplementedError()
