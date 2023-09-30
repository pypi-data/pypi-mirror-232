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
from typing import Any, Dict, Optional, Union

import torch
import torch.distributed as distributed
from peft import LoraConfig  # type: ignore
from transformers import (
    BitsAndBytesConfig,
    GPTQConfig,
    PreTrainedModel,
    PreTrainedTokenizer,
    TrainingArguments,
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
from ..datasets.base import BaseDataset
from ..trainers.lm import LMTrainer
from ..utils.logger import dist_logger
from ..utils.miscellaneous import is_distributed_training
from ..utils.nn import apply_lora, stabilize_training
from ..utils.post_training import post_training


class BaseExperiment:
    def __init__(self, config: HuggingFaceConfig):
        self.at_beggining()

        self.config = config

        self.save_config()
        dist_logger.info("Config saved")

        self.before_checks()
        self.checks()
        dist_logger("Checks passed successfully")
        self.after_checks()

        self.before_training_arguments_build()
        self.training_arguments = self.build_training_arguments()
        dist_logger(f"Training arguments was built:\n{self.training_arguments.to_json_string()}")
        self.after_training_arguments_build()

        self.before_train_dataset_build()
        self.train_dataset = self.build_train_dataset()
        dist_logger(f"Train dataset {self.train_dataset.__class__.__name__} was built. Size: {len(self.train_dataset)}")
        self.after_train_dataset_build()

        self.before_valid_dataset_build()
        self.valid_dataset = self.build_valid_dataset()
        if self.valid_dataset is not None:
            dist_logger(
                f"Valid dataset {self.valid_dataset.__class__.__name__} was built. Size: {len(self.valid_dataset)}"
            )
        else:
            dist_logger("Valid dataset is None")
        self.after_train_dataset_build()

        self.before_tokenizer_build()
        self.tokenizer = self.build_tokenizer()
        dist_logger(f"Tokenizer {self.config.correct_tokenizer_name_or_path} was built")
        self.after_tokenizer_build()

        self.before_collator_build()
        self.collator = self.build_collator()
        dist_logger(f"Collator {self.collator.__class__.__name__} was built")
        self.after_collator_build()

        self.before_quantization_config_build()
        self.quantization_config = self.build_quantization_config()
        if self.quantization_config is not None:
            dist_logger(f"Quantization config was built:\n{self.quantization_config.to_json_string()}")
        else:
            dist_logger(f"Quantization config is None. Model will be loaded using {config.dtype}")
        self.after_quantization_config_build()

        self.before_model_build()
        self.model = self.build_model()
        dist_logger(f"Model {config.model_name_or_path} was built")
        self.after_model_build()

        self.before_lora_apply()
        if self.config.apply_lora:
            self.lora_config: Optional[LoraConfig] = self.apply_lora()
            dist_logger(f"LoRA {config.model_name_or_path} applied")
        else:
            self.lora_config = None
        self.after_lora_apply()

        self.before_stabilize_training()
        if config.stabilize:
            self.stabilize_training()
            dist_logger("Model stabilized for training")
        self.after_stabilize_training()

        self.before_trainer_build()
        self.trainer = self.build_trainer()
        dist_logger(f"Trainer {self.trainer.__class__.__name__} was built")
        self.after_trainer_build()

        dist_logger("Init complete")

    # checks

    def before_checks(self) -> None:
        return None

    def checks(self) -> None:
        if not torch.cuda.is_available():
            dist_logger.warning("CUDA is not available")

        self.config.check()

        return None

    def after_checks(self) -> None:
        return None

    # training arguments

    def before_training_arguments_build(self) -> None:
        return None

    def build_training_arguments(self) -> TrainingArguments:
        training_arguments = build_training_arguments(config=self.config)
        return training_arguments

    def after_training_arguments_build(self) -> None:
        return None

    # train_dataset

    def before_train_dataset_build(self) -> None:
        return None

    def build_train_dataset(self) -> BaseDataset:
        dataset = build_dataset(config=self.config, is_train=True)
        if dataset is None:
            raise ValueError("Train dataset can't be loaded")
        return dataset

    def after_train_dataset_build(self) -> None:
        return None

    # valid_dataset

    def before_valid_dataset_build(self) -> None:
        return None

    def build_valid_dataset(self) -> Optional[BaseDataset]:
        dataset = build_dataset(config=self.config, is_train=False)
        return dataset

    def after_valid_dataset_build(self) -> None:
        return None

    # tokenizer

    def before_tokenizer_build(self) -> None:
        return None

    def build_tokenizer(self) -> PreTrainedTokenizer:
        tokenizer = build_tokenizer(config=self.config, use_fast=self.config.tokenizer_use_fast)
        return tokenizer

    def after_tokenizer_build(self) -> None:
        return None

    # collator

    def before_collator_build(self) -> None:
        return None

    def build_collator(self) -> BaseCollator:
        collator = build_collator(config=self.config, tokenizer=self.tokenizer)
        return collator

    def after_collator_build(self) -> None:
        return None

    # quantization_config

    def before_quantization_config_build(self) -> None:
        return None

    def build_quantization_config(self) -> Union[BitsAndBytesConfig, GPTQConfig, None]:
        quantization_config = build_quantization_config(config=self.config)
        return quantization_config

    def after_quantization_config_build(self) -> None:
        return None

    # model

    def before_model_build(self) -> None:
        return None

    def build_model(self) -> PreTrainedModel:
        model = build_model(config=self.config, quantization_config=self.quantization_config)
        return model

    def after_model_build(self) -> None:
        return None

    # lora

    def before_lora_apply(self) -> None:
        return None

    def apply_lora(self) -> LoraConfig:
        self.model, lora_config = apply_lora(config=self.config, model=self.model)
        return lora_config

    def after_lora_apply(self) -> None:
        return None

    # stabilize_training

    def before_stabilize_training(self) -> None:
        return None

    def stabilize_training(self) -> None:
        self.model = stabilize_training(model=self.model)

    def after_stabilize_training(self) -> None:
        return None

    # trainer

    def before_trainer_build(self) -> None:
        return None

    def build_additional_trainer_kwargs(self) -> Dict[str, Any]:
        return dict()

    def build_trainer(self) -> LMTrainer:
        additional_trainer_kwargs = self.build_additional_trainer_kwargs()

        trainer = build_trainer(
            config=self.config,
            pad_token_id=self.tokenizer.pad_token_id,
            training_arguments=self.training_arguments,
            model=self.model,
            train_dataset=self.train_dataset,
            collator=self.collator,
            valid_dataset=self.valid_dataset,
            **additional_trainer_kwargs,
        )

        return trainer

    def after_trainer_build(self) -> None:
        return None

    def save_config(self) -> None:
        json_config = json.dumps(self.config.__dict__, indent=2)
        dist_logger(f"Config:\n{json_config}")

        if is_distributed_training():
            if distributed.get_rank() == self.config.local_rank:
                os.makedirs(self.config.output_dir, exist_ok=True)
                with open(os.path.join(self.config.output_dir, "training_config.json"), "w") as file_object:
                    file_object.write(json_config)
        else:
            os.makedirs(self.config.output_dir, exist_ok=True)
            with open(os.path.join(self.config.output_dir, "training_config.json"), "w") as file_object:
                file_object.write(json_config)

        return None

    def before_train(self) -> None:
        return None

    def train(self):
        self.before_train()

        dist_logger("Training will start soon")
        self.trainer.train()
        dist_logger("Training end")

        self.after_train()

        if is_distributed_training():
            if distributed.get_rank() == self.config.local_rank:
                post_training(config=self.config, tokenizer=self.tokenizer)
        else:
            post_training(config=self.config, tokenizer=self.tokenizer)

        dist_logger(f"Model saved to {self.training_arguments.output_dir}")

        self.at_end()

    def after_train(self) -> None:
        return None

    def at_beggining(self) -> None:
        return None

    def at_end(self) -> None:
        return None
