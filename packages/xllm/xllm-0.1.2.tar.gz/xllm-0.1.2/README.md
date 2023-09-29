# 🦖 X—LLM: Simple & Cutting Edge LLM Finetuning

<div align="center">

[![Build](https://github.com/KompleteAI/xllm/actions/workflows/build.yaml/badge.svg?branch=main)](https://github.com/KompleteAI/xllm/actions/workflows/build.yaml)
[![Github: License](https://img.shields.io/github/license/KompleteAI/xllm.svg?color=blue)](https://github.com/KompleteAI/xllm/blob/main/LICENSE)
[![Github: Release](https://img.shields.io/github/v/release/kompleteai/xllm.svg)](https://github.com/KompleteAI/xllm/releases)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/modelfront/predictor/blob/master/.pre-commit-config.yaml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/KompleteAI/xllm/graph/badge.svg?token=ZOBMDXVW4B)](https://codecov.io/gh/KompleteAI/xllm)

Simple & cutting edge LLM finetuning using the most advanced methods (QLoRA, DeepSpeed, GPTQ, Flash Attention 2, FSDP,
etc)

</div>

## Features

- Train LLM's easily
- Simply add QLoRA, DeepSpeed
- Track your progress using W&B
- Easy to extend and integrate to your project

## Before we start

## Table of Contents

# What problem does X—LLM solve?

## Efficient finetune

See benchmark later

## Fusing LoRA

## GPTQ Quantization

## Extend with your data, collator and trainer

# Projects using X—LLM

Shurale
some

## Quickstart ⚡

## Install

## Examples

### Finetune Llama 7b

### Finetune Falcon 180b

# How to use in your project

## Prepare

## Data

## Collator

## Trainer

# Training Benchmark

> RTX 4090 have 24 Gb, so 4 RTX 4090 have 24 Gb * 4 = 96 Gb

## Full Finetune

<details>
<summary>Single RTX 4090, Full Finetune</summary>
</details>

<details>
<summary>4 RTX 4090, Full Finetune, DeepSpeed Stage 1</summary>
</details>

<details>
<summary>4 RTX 4090, Full Finetune, DeepSpeed Stage 2</summary>
</details>

<details>
<summary>4 RTX 4090, Full Finetune, DeepSpeed Stage 3</summary>
</details>

<details>
<summary>4 RTX 4090, Full Finetune, FSDP</summary>
</details>

## LoRA

<details>
<summary>Single RTX 4090, LoRA</summary>
</details>

<details>
<summary>4 RTX 4090, LoRA, DeepSpeed Stage 1</summary>
</details>

<details>
<summary>4 RTX 4090, LoRA, DeepSpeed Stage 2</summary>
</details>

<details>
<summary>4 RTX 4090, LoRA, DeepSpeed Stage 3</summary>
</details>

<details>
<summary>4 RTX 4090, LoRA, FSDP</summary>
</details>

# Badge

Building something cool with X—LLM? Consider adding a badge to your model card.

```bash
[<img src="https://github.com/KompleteAI/xllm/blob/main/static/images/xllm-badge.png" alt="Powered by X—LLM" width="175" height="32"/>](https://github.com/KompleteAI/xllm)
```

[<img src="https://github.com/KompleteAI/xllm/blob/main/static/images/xllm-badge.png" alt="Powered by X—LLM" width="175" height="32"/>](https://github.com/KompleteAI/xllm)

# Lack of tests

# Future Work

- GPU CI using RunPod
- Add multipacking

## Call to action

If you like this library, please help me find a job
