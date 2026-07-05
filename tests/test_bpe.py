import unittest

from tokenizer.bpe import BPE


class TestBPE(unittest.TestCase):
    def test_train_is_deterministic(self) -> None:
        corpus = [
            "low lower newest widest",
            "low low lower",
        ]
        tok1 = BPE()
        tok2 = BPE()
        tok1.train(corpus, vocab_size=30)
        tok2.train(corpus, vocab_size=30)
        self.assertEqual(tok1.merges, tok2.merges)

    def test_round_trip_on_training_text(self) -> None:
        corpus = [
            "low lower newest widest",
            "tokenizer basics are fun",
        ]
        tok = BPE()
        tok.train(corpus, vocab_size=30)
        text = "low newest widest"
        self.assertEqual(tok.decode(tok.encode(text)), text)


if __name__ == "__main__":
    unittest.main()
