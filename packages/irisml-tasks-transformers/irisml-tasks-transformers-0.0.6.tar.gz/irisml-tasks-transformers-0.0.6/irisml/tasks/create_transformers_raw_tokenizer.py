import dataclasses
import typing
import torch
from transformers import AutoTokenizer
import irisml.core


class Task(irisml.core.TaskBase):
    """Create a Tokenizer using transformers library. Return the tokenizer as-is.
    """
    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Config:
        name: str

    @dataclasses.dataclass
    class Outputs:
        tokenizer: typing.Callable

    def execute(self, inputs):
        # TODO: Load from Azure Blob.
        tokenizer = AutoTokenizer.from_pretrained(self.config.name)
        return self.Outputs(tokenizer)

    def dry_run(self, inputs):
        return self.Outputs(fake_tokenizer)


def fake_tokenizer(*args, **kwargs):
    return torch.zeros(1, 77, dtype=torch.long)
