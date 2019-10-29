# Copyright 2019 Neural Networks and Deep Learning lab, MIPT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional, Union, Dict

from deeppavlov.skills.dsl_skill.utils import UserId


class UserContext:
    """
    UserContext object stores information that the current skill currently knows about the user.

    Args:
        user_id: id of user
        message: current message
        current_state: current user state
        payload: custom payload dictionary, or a JSON-serialized string of such dictionary

    Attributes:
        handler_payload: stores information generated by the selected handler

    """

    def __init__(
            self,
            user_id: Optional[UserId] = None,
            message: Optional[str] = None,
            current_state: Optional[str] = None,
            payload: Optional[Union[Dict, str]] = None,
    ):
        self.user_id = user_id
        self.message = message
        self.current_state = current_state
        self.handler_payload = {}

        # some custom data added by skill creator
        self.payload = payload
        if payload == '' or payload is None:
            self.payload = {}
        elif isinstance(payload, str):
            self.payload = json.loads(payload)
