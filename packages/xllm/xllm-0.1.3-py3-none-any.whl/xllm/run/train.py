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

import json
import os
from typing import Optional, Tuple, Union

import torch
import torch.distributed as distributed
from peft import LoraConfig  # type: ignore
from transformers import (
    BitsAndBytesConfig,
    GPTQConfig,
    Trainer,
)

from ..collators.base import BaseCollator
from ..core.config import HuggingFaceConfig
from ..core.dependencies import (
    build_collator,
    build_dataset,
    build_model,
    build_quantization_config,
    build_tokenizer,
    build_trainer,
    build_training_arguments,
)
from ..utils.logger import dist_logger
from ..utils.miscellaneous import is_distributed_training
from ..utils.post_training import post_training


def train(
    config: HuggingFaceConfig,
) -> Tuple[BaseCollator, Union[BitsAndBytesConfig, GPTQConfig, None], Optional[LoraConfig], Trainer,]:
    if not torch.cuda.is_available():
        dist_logger.warning("CUDA is not available")

    json_config = json.dumps(config.__dict__, indent=2)
    dist_logger(f"Config:\n{json_config}")

    if is_distributed_training():
        if distributed.get_rank() == config.local_rank:
            os.makedirs(config.output_dir, exist_ok=True)
            with open(os.path.join(config.output_dir, "training_config.json"), "w") as file_object:
                file_object.write(json_config)
    else:
        os.makedirs(config.output_dir, exist_ok=True)
        with open(os.path.join(config.output_dir, "training_config.json"), "w") as file_object:
            file_object.write(json_config)

    config.check()
    dist_logger("Checks completed successfully")

    training_arguments = build_training_arguments(config=config)
    dist_logger(f"Training arguments was built:\n{training_arguments.to_json_string()}")

    train_dataset = build_dataset(config=config, is_train=True)
    dist_logger(f"Train dataset {train_dataset.__class__.__name__} was built")

    if train_dataset is None:
        raise ValueError("Train dataset can't be loaded")

    valid_dataset = build_dataset(config=config, is_train=False)
    if valid_dataset is not None:
        dist_logger(f"Valid dataset {valid_dataset.__class__.__name__} was built")
    else:
        dist_logger("Valid dataset is None")

    tokenizer = build_tokenizer(config=config)
    dist_logger(f"Tokenizer {config.correct_tokenizer_name_or_path} was built")

    collator = build_collator(config=config, tokenizer=tokenizer)
    dist_logger(f"Collator {collator.__class__.__name__} was built")

    quantization_config = build_quantization_config(config=config)
    if quantization_config is not None:
        dist_logger(f"Quantization config was built:\n{quantization_config.to_json_string()}")
    else:
        dist_logger(f"Quantization config is None. Model will be loaded using {config.dtype}")

    model, lora_config = build_model(config=config, quantization_config=quantization_config)
    dist_logger(f"Model {config.model_name_or_path} was built")

    trainer = build_trainer(
        config=config,
        pad_token_id=tokenizer.pad_token_id,
        training_arguments=training_arguments,
        model=model,
        train_dataset=train_dataset,
        valid_dataset=valid_dataset,
        collator=collator,
    )
    dist_logger(f"Trainer {trainer.__class__.__name__} was built")

    dist_logger("Training will start soon")
    trainer.train()
    dist_logger("Training end")

    if is_distributed_training():
        if distributed.get_rank() == config.local_rank:
            post_training(config=config, tokenizer=tokenizer)
    else:
        post_training(config=config, tokenizer=tokenizer)

    dist_logger(f"Model saved to {training_arguments.output_dir}")

    return collator, quantization_config, lora_config, trainer
