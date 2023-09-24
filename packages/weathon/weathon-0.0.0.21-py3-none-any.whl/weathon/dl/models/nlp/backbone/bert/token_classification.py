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
from weathon.dl.registry import MODELS
from weathon.dl.utils.constants import Tasks
from weathon.dl.utils.constants.metainfo import Heads, Models
from weathon.dl.models.nlp.task_models.token_classification import (
    ModelForTokenClassification, ModelForTokenClassificationWithCRF)
from weathon.dl.utils import logger as logging

logger = logging.get_logger()


@MODELS.register_module(Tasks.token_classification, module_name=Models.bert)
@MODELS.register_module(Tasks.part_of_speech, module_name=Models.bert)
@MODELS.register_module(Tasks.word_segmentation, module_name=Models.bert)
class BertForTokenClassification(ModelForTokenClassification):
    r"""Bert Model with a token classification head on top (a linear layer on top of
    the hidden-states output) e.g. for Named-Entity-Recognition (NER) tasks, word-segmentation.

    This model inherits from :class:`TokenClassificationModel`. Check the superclass documentation for the generic
    methods the library implements for all its model (such as downloading or saving, resizing the input embeddings,
    pruning heads etc.)

    This model is also a PyTorch `torch.nn.Module <https://pytorch.org/docs/stable/nn.html#torch.nn.Module>`__
    subclass. Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to
    general usage and behavior.

    """

    base_model_type = 'bert'
