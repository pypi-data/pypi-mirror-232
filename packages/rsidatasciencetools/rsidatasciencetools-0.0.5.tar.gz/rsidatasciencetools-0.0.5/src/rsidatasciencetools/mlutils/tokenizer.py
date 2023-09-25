'''custom wrappers for tokenizing and cleaning strings'''
import pathlib
import re
import os
from typing import List
from warnings import warn

# import tensorflow_datasets as tfds
import tensorflow_text as text
import tensorflow as tf

from tensorflow_text.tools.wordpiece_vocab import bert_vocab_from_dataset as bert_vocab
# from tensorflow_text.tools import wordpiece_vocab


bert_tokenizer_params = dict(lower_case=True)
reserved_tokens = ["[PAD]", "[UNK]", "[START]", "[END]"]
bert_vocab_args = dict(
    # The target vocabulary size
    vocab_size = 12000,
    # Reserved tokens that must be included in the vocabulary
    reserved_tokens=reserved_tokens,
    # Arguments for `text.BertTokenizer`
    bert_tokenizer_params=bert_tokenizer_params,
    # Arguments for `wordpiece_vocab.wordpiece_tokenizer_learner_lib.learn`
    learn_params={
        'max_token_length':12
    },
)


def create_vocab(examples, vocab_args=bert_vocab_args):
    record_vocab = bert_vocab.bert_vocab_from_dataset(
        examples.batch(1000).prefetch(2),
        **vocab_args
    )
    return record_vocab


def write_vocab(vocab, filepath='rec_data_vocab.txt'):
    try:
        with open(filepath, 'w') as f:
            for token in vocab:
                print(token, file=f)
    except IOError:
        return
    return filepath


def read_vocab(fname='rec_data_vocab.txt'):
    if not(os.path.exists(fname)):
        return
    with open(fname,'r') as f:
        record_vocab = [string for string in f.read().split('\n') if string]
    return record_vocab


def build_subwords_tokenizer(vocab_file='rec_data_vocab.large.txt', 
                    basic=False, load=False, save_model_name='rec_data_token_converter', 
                    maxn=3, train_examples=None, update_bert_params=None):
    ''' build the sub-words tokenizer 
            - generate vocab from training examples
            - instantiate the Tokenizer
            - save if requested
        Args:
            vocab_file='rec_data_vocab.large.txt' if the file is not found, it will be 
                generated from the training examples and saved to the filename provided
            basic=False use a basic tokenizer with the custom start/end tag and other
                pre/post processing and cleaning routines
            load=False load tokenizer from file `save_model_name`
            save_model_name='rec_data_token_converter' the load/save filename
            maxn=6 maximum number of characters to use per token
            train_examples=None tf.Dataset object used for extracting the vocabulary
            update_bert_params=None dictionary of updated tokenizer params (associate with
                text.BertTokenizer class)
    '''
    record_vocab = None
    load = load and os.path.exists(save_model_name)

    if not(os.path.exists(vocab_file)) and not(load):
        assert train_examples is not None, (
            "vocab file does not exist, and example not provided with which to generate it")
        record_vocab = create_vocab(train_examples)
        vocab_file = write_vocab(record_vocab)
        assert vocab_file is not None, 'unable to create vocab file'

    bert_tokenizer_params.update(dict(max_chars_per_token=maxn))  # ), min_chars_per_token=maxn))
    if update_bert_params:
        bert_tokenizer_params.update(update_bert_params)
    if load:
        tf_module = tf.saved_model.load(save_model_name)
        if 'Custom' not in tf_module.__class__.__name__:
            rec_tokenizer = tf_module
        else:
            rec_tokenizer = tf_module.start
    elif basic:
        rec_tokenizer = text.BertTokenizer(vocab_file, **bert_tokenizer_params)
    else:
        tf_module = tf.Module() 
        tf_module.start = CustomTokenizer(reserved_tokens, vocab_file, **bert_tokenizer_params)
        tf_module.end = CustomTokenizer(reserved_tokens, vocab_file, **bert_tokenizer_params)
        rec_tokenizer = tf_module.start

    if train_examples is not None:
        for examples in train_examples.batch(3).take(1):
            for ex in examples:
                print(ex.numpy())
        # Tokenize the examples -> (batch, word, word-piece)
        token_batch = rec_tokenizer.tokenize(examples)
        # Merge the word and word-piece axes -> (batch, tokens)
        token_batch = token_batch.merge_dims(-2,-1)

        for ex in token_batch.to_list():
            print(ex)
        if record_vocab is None:
            record_vocab = read_vocab(vocab_file)
        # Lookup each token id in the vocabulary.
        txt_tokens = tf.gather(record_vocab, token_batch)
        # Join with spaces.
        tf.strings.reduce_join(txt_tokens, separator=' ', axis=-1)
    if save_model_name is not None:
        if basic:
            warn('basic tokenizer option is not embeddd in tf.Module and cannot be saved')
        else:
            tf.saved_model.save(tf_module, save_model_name)
    if basic:
        return rec_tokenizer
    else:
        return tf_module


class CustomTokenizer(tf.Module):
    def __init__(self, reserved_tokens:List[str], vocab_path, **kwargs):
        if 'lower_case' not in kwargs:
            kwargs['lower_case'] = True
        self.tokenizer = text.BertTokenizer(vocab_path, **kwargs)
        self._reserved_tokens = reserved_tokens
        self._vocab_path = tf.saved_model.Asset(vocab_path)

        vocab = pathlib.Path(vocab_path).read_text().splitlines()
        self.vocab = tf.Variable(vocab)

        ## Create the signatures for export:   

        # Include a tokenize signature for a batch of strings. 
        self.tokenize.get_concrete_function(
            tf.TensorSpec(shape=[None], dtype=tf.string))

        # Include `detokenize` and `lookup` signatures for:
        #   * `Tensors` with shapes [tokens] and [batch, tokens]
        #   * `RaggedTensors` with shape [batch, tokens]
        self.detokenize.get_concrete_function(
            tf.TensorSpec(shape=[None, None], dtype=tf.int64))
        self.detokenize.get_concrete_function(
              tf.RaggedTensorSpec(shape=[None, None], dtype=tf.int64))

        self.lookup.get_concrete_function(
            tf.TensorSpec(shape=[None, None], dtype=tf.int64))
        self.lookup.get_concrete_function(
              tf.RaggedTensorSpec(shape=[None, None], dtype=tf.int64))

        # These `get_*` methods take no arguments
        self.get_vocab_size.get_concrete_function()
        self.get_vocab_path.get_concrete_function()
        self.get_reserved_tokens.get_concrete_function()
    
    @staticmethod
    def add_start_end(ragged):
        START = tf.argmax(tf.constant(reserved_tokens) == "[START]")
        END = tf.argmax(tf.constant(reserved_tokens) == "[END]")
        count = ragged.bounding_shape()[0]
        starts = tf.fill([count,1], START)
        ends = tf.fill([count,1], END)
        return tf.concat([starts, ragged, ends], axis=1)
    
    @staticmethod
    def cleanup_text(reserved_tokens, token_txt):
        # Drop the reserved tokens, except for "[UNK]".
        bad_tokens = [re.escape(tok) for tok in reserved_tokens if tok != "[UNK]"]
        bad_token_re = "|".join(bad_tokens)

        bad_cells = tf.strings.regex_full_match(token_txt, bad_token_re)
        result = tf.ragged.boolean_mask(token_txt, ~bad_cells)

        # Join them into strings.
        result = tf.strings.reduce_join(result, separator=' ', axis=-1)

        return result
    
    @tf.function
    def tokenize(self, strings):
        enc = self.tokenizer.tokenize(strings)
        # Merge the `word` and `word-piece` axes.
        enc = enc.merge_dims(-2,-1)
        enc = self.add_start_end(enc)
        return enc

    @tf.function
    def detokenize(self, tokenized):
        words = self.tokenizer.detokenize(tokenized)
        return CustomTokenizer.cleanup_text(self._reserved_tokens, words)

    @tf.function
    def lookup(self, token_ids):
        return tf.gather(self.vocab, token_ids)

    @tf.function
    def get_vocab_size(self):
        return tf.shape(self.vocab)[0]

    @tf.function
    def get_vocab_path(self):
        return self._vocab_path

    @tf.function
    def get_reserved_tokens(self):
        return tf.constant(self._reserved_tokens)