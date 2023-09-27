from datasets import load_dataset

from keras_gpt.tokenizer import Tokenizer

if __name__ == "__main__":
    dataset = load_dataset("tiny_shakespeare")

    tokenizer = Tokenizer()
    tokenizer.train(corpus=dataset["train"][0]["text"], target_vocab_size=5000)
    tokenizer.dump_vocab("vocab.json")
    tokenizer.dump_merge_rules("merge_rules.json")

    tokenizer = Tokenizer(vocab_file="vocab.json", merge_rules_file="merge_rules.json")
    print(tokenizer.encode("Sir, I shall tell you."))
    print(tokenizer.decode(tokenizer.encode("Sir, I shall tell you.")))
