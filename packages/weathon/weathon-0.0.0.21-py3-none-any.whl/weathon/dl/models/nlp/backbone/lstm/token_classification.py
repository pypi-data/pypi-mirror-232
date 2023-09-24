# Copyright 2018 The Google AI Language Team Authors and The HuggingFace Inc. team.
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
# All rights reserved.
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

from weathon.dl.utils.constants.metainfo import Heads, Models
from weathon.dl.registry import MODELS
from weathon.dl.models.nlp.task_models import (
    ModelForTokenClassification, ModelForTokenClassificationWithCRF)
from weathon.dl.utils import logger as logging
from weathon.dl.utils.constants import Tasks

logger = logging.get_logger()


@MODELS.register_module(Tasks.token_classification, module_name=Models.lcrf)
@MODELS.register_module(
    Tasks.named_entity_recognition, module_name=Models.lcrf)
@MODELS.register_module(Tasks.part_of_speech, module_name=Models.lcrf)
@MODELS.register_module(Tasks.word_segmentation, module_name=Models.lcrf)
@MODELS.register_module(Tasks.word_segmentation, module_name=Models.lcrf_wseg)
class LSTMForTokenClassificationWithCRF(ModelForTokenClassificationWithCRF):
    r"""Model with a token classification head on top (a linear layer on top of
    the hidden-states output) e.g. for Named-Entity-Recognition (NER) tasks, word-segmentation.

    """
    override_base_model_type = True
    base_model_type = Models.lstm
    head_type = Heads.lstm_crf

    def parse_head_cfg(self):
        head_cfg = super(ModelForTokenClassification, self).parse_head_cfg()
        head_cfg['hidden_size'] = (
            head_cfg.hidden_size
            if hasattr(head_cfg, 'hidden_size') else head_cfg.lstm_hidden_size)
        head_cfg['num_labels'] = self.config.num_labels
        return head_cfg
