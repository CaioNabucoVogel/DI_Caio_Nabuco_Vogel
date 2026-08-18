def add_tokens(self, new_tokens: str | AddedToken | Sequence[str | AddedToken], special_tokens: bool=False) -> int:
    """
        #TODO remove this from here! PreTrainedTOkeniuzerBase should be agnostic of AddedToken.

        Add a list of new tokens. If the new tokens are not in the vocabulary, they are added to the end. Added tokens and
        tokens from the vocabulary of the tokenization algorithm are therefore not treated in the same way.

        Args:
            new_tokens (`str`, `tokenizers.AddedToken` or a sequence of *str* or `tokenizers.AddedToken`):
                Tokens are only added if they are not already in the vocabulary. `tokenizers.AddedToken` wraps a string
                token to let you personalize its behavior: whether this token should only match against a single word,
                whether this token should strip all potential whitespaces on the left side, whether this token should
                strip all potential whitespaces on the right side, etc.
            special_tokens (`bool`, *optional*, defaults to `False`):
                Specifies if the token is special. This mostly changes the normalization behavior
                See details for `tokenizers.AddedToken` in HuggingFace tokenizers library.

        Returns:
            `int`: Number of tokens added to the vocabulary.

        Examples:

        ```python
        # Let's see how to increase the vocabulary of Bert model and tokenizer
        tokenizer = BertTokenizerFast.from_pretrained("google-bert/bert-base-uncased")
        model = BertModel.from_pretrained("google-bert/bert-base-uncased")

        num_added_toks = tokenizer.add_tokens(["new_tok1", "my_new-tok2"])
        print("We have added", num_added_toks, "tokens")
        # Notice: resize_token_embeddings expect to receive the full size of the new vocabulary, i.e., the length of the tokenizer.
        model.resize_token_embeddings(len(tokenizer))
        ```"""
    if not new_tokens:
        return 0
    if not isinstance(new_tokens, (list, tuple)):
        new_tokens = [new_tokens]
    return self._add_tokens(new_tokens, special_tokens=special_tokens)