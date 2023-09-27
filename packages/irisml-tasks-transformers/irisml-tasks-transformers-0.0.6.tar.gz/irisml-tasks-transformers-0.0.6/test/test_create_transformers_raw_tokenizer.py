import unittest
from irisml.tasks.create_transformers_raw_tokenizer import Task


class TestCreateTransformersRawTokenizer(unittest.TestCase):
    def test_simple(self):
        outputs = Task(Task.Config('openai/clip-vit-base-patch32')).execute(Task.Inputs())
        self.assertIsNotNone(outputs.tokenizer)

        token = outputs.tokenizer("Answer to the Ultimate Question of Life, The Universe, and Everything")
        self.assertGreater(len(token), 0)
        self.assertIsInstance(token.input_ids, list)
        self.assertIsInstance(token.attention_mask, list)
