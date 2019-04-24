from pathlib import Path
from typing import Union
from typing import Tuple, Optional, List
from logging import getLogger
import aiml
import uuid
from deeppavlov.core.common.registry import register
from deeppavlov.core.skill.skill import Skill
log = getLogger(__name__)


@register("aiml_skill")
class AIMLSkill(Skill):
    """Skill wraps python-aiml library into DeepPavlov interfrace.
    AIML uses directory with AIML scripts which are loaded at initialization and used as patterns
    for answering at each step.
    """

    def __init__(self,
                 path_to_aiml_scripts: Union[str, None] = None,
                 positive_confidence: float = 0.66,
                 null_response: str = "I don't know",
                 null_confidence: float = 0.33
                 ) -> None:
        """
        Construct skill:
            read AIML scripts,
            load AIML kernel

        Args:
            path_to_aiml_scripts: string path to folder with AIML scripts
            null_response: Response string to answer if no AIML Patterns matched
            positive_confidence: The confidence of response if response was found in AIML scripts
            null_confidence: The confidence when AIML scripts has no rule for responding and system returns null_response
        """

        if not path_to_aiml_scripts:
            cur_dir = Path(__file__).absolute().parent
            self.path_to_aiml_scripts = cur_dir.joinpath("aiml_scripts")
            log.warning(f"path_to_aiml_scripts is not provided, use default path: `{self.path_to_aiml_scripts}`")
        else:
            self.path_to_aiml_scripts = Path(path_to_aiml_scripts)
            log.info(f"path_to_aiml_scripts is: `{self.path_to_aiml_scripts}`")

        self.positive_confidence = positive_confidence
        self.null_confidence = null_confidence
        self.null_response = null_response
        self.kernel = aiml.Kernel()
        # to block AIML output:
        self.kernel._verboseMode = False
        self._load_scripts()

    def _load_scripts(self) -> None:
        """
        Scripts are loaded recursively from files with extensions .xml and .aiml
        Returns: None

        """
        # learn kernel to all aimls in directory tree:
        all_files = sorted(self.path_to_aiml_scripts.rglob('*.*'))
        for each_file_path in all_files:
            if each_file_path.suffix in ['.aiml', '.xml']:
                # learn the script file
                self.kernel.learn(str(each_file_path))

    def process_step(self, utterance_str: str, user_id: any) -> Tuple[str, float]:
        response = self.kernel.respond(utterance_str, sessionID=user_id)
        # here put your estimation of confidence:
        if response:
            # print(f"AIML responds: {response}")
            confidence = self.positive_confidence
        else:
            # print("AIML responses silently...")
            response = self.null_response
            confidence = self.null_confidence
        return response, confidence

    def _generate_user_id(self) -> str:
        """
        Here you put user id generative logic if you want to implement it in the skill.

        Although it is better to delegate user_id generation to Agent Layer
        Returns: int

        """
        return uuid.uuid1()

    def __call__(self, utterances_batch: list, history_batch: list, states_batch: list) -> Tuple[list, list, list]:
        """Returns skill inference result.

        Returns batches of skill inference results, estimated confidence
        levels and up to date states corresponding to incoming utterance
        batch.

        Args:
            utterances_batch: A batch of utterances of str type.
            history_batch: A batch of list typed histories for each utterance.
            states_batch:  A batch of arbitrary typed states for
                each utterance.


        Returns:
            response: A batch of arbitrary typed skill inference results.
            confidence: A batch of float typed confidence levels for each of
                skill inference result.
            output_states_batch:  A batch of arbitrary typed states for
                each utterance.

        """
        # grasp user_ids from states batch.
        # We expect that skill receives None or dict of state for each utterance.
        # if state has user_id then skill uses it, otherwise it generates user_id and calls the
        # user with this name in further.

        # In this implementation we use current datetime for generating uniqe ids
        output_states_batch = []
        user_ids = []
        for each_state in states_batch:
            if not each_state:
                user_id = self._generate_user_id()
                new_state = {'user_id': user_id}

            elif 'user_id' not in each_state:
                new_state = each_state
                user_id = self._generate_user_id()
                new_state['user_id'] = self._generate_user_id()

            else:
                new_state = each_state
                user_id = new_state['user_id']

            user_ids.append(user_id)
            output_states_batch.append(new_state)

        confident_responses = map(self.process_step, utterances_batch, user_ids)
        responses_batch, confidences_batch = zip(*confident_responses)

        return responses_batch, confidences_batch, output_states_batch
