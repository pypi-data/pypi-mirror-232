# Copyright 2023 Komplete AI Team. All rights reserved.
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

from typing import Optional, Tuple, Type, Union

from peft import LoraConfig  # type: ignore
from transformers import (
    BitsAndBytesConfig,
    GPTQConfig,
    HfArgumentParser,
    Trainer,
)

from ..collators.base import BaseCollator
from ..core.config import HuggingFaceConfig
from ..run.train import train
from ..utils.cli import setup_cli


def cli_run_train(
    config_cls: Type[HuggingFaceConfig] = HuggingFaceConfig,
) -> Tuple[BaseCollator, Union[BitsAndBytesConfig, GPTQConfig, None], Optional[LoraConfig], Trainer,]:
    parser = HfArgumentParser(config_cls)
    config = parser.parse_args_into_dataclasses()[0]
    setup_cli(config=config, logger_path="./xllm_train.log")
    collator, quantization_config, lora_config, trainer = train(config=config)
    return collator, quantization_config, lora_config, trainer


if __name__ == "__main__":
    cli_run_train(config_cls=HuggingFaceConfig)
