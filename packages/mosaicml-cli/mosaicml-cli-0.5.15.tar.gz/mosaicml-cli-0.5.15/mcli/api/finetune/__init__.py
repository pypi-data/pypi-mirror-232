"""Finetuning APIs"""
from mcli.api.finetune.api_finetune import finetune
from mcli.api.finetune.api_instruction_finetune import instruction_finetune

__all__ = [
    "finetune",
    "instruction_finetune",
]
