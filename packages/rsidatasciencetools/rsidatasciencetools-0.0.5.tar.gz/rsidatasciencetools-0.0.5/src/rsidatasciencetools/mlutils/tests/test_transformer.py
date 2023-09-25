''' run some basic tests on the transformer module'''
from os import path
from warnings import warn
import numpy as np
from rsidatasciencetools.config.baseconfig import YmlConfig
from rsidatasciencetools.datautils.datagen import gen_records_from_data
from rsidatasciencetools.datautils.formsource import gen_noisy_documents_from_records

test_path = path.join(path.abspath(path.dirname(__file__)), 
            '..', '..', 'datautils', 'tests')


def test_transformer_embedding_test(debug=1):
    try:
        import tensorflow as tf
        from rsidatasciencetools.mlutils.text import get_text_data_from_records
        from rsidatasciencetools.mlutils.tokenizer import build_tokenizer
        from rsidatasciencetools.mlutils.transformer import (Transformer,
            CustomSchedule, Translator, masked_accuracy, masked_loss, 
            print_translation, default_transformer_params, make_transformer_batches)
        from rsidatasciencetools.mlutils.tokenizer import build_subwords_tokenizer
    except ImportError as ie:
        if 'tensorflow' in str(ie):
            assert True
            warn(f'could not find "tensorflow" library, skipping test | {str(ie)}')
            return            
        else:
            raise(ie)
        
    yml = YmlConfig(path.join(test_path, 'embed_tf.yml'), auto_update_paths=True, debug=2)
    tokenizers = train_examples = val_examples = None 

    if not(isinstance(yml,YmlConfig)):
        yml = YmlConfig(yml, auto_update_paths=True, debug=2)

    if train_examples is None and val_examples is None:
        
        yml_md = YmlConfig(path.join(test_path, 'MD_rec_gen.yml'), auto_update_paths=True, debug=2)
        df, yml_md = gen_records_from_data(yml_md, numrec=2000, seed=42, 
            add_unique_label=True, as_df=True, debug=debug)
        df_corrupted, yml_md = gen_noisy_documents_from_records(yml_md, df,
            as_df=True, prob_e=0.05,seed=45,debug=debug)
        yml, DATASET_SIZE, full_dataset, train_examples, _, _ = get_text_data_from_records(
                yml, in_df=df, split=False, shuffle=None, debug=debug)
        
        yml, DATASET_SIZE, full_dataset_test, _, _, _ = get_text_data_from_records(
            yml, in_df=df, split=False, shuffle=None, debug=debug)

    if tokenizers is None:
        tokenizers = build_subwords_tokenizer(vocab_file=yml['vocab_file'],
                        load=True, save_model_name=yml['tokenizer_model_name'], 
                        maxn=yml['maxn'], train_examples=full_dataset)

    lengths = []
    for examples in train_examples.batch(2048):
        if isinstance(examples,tuple):
            st, end = examples
            tokens = tokenizers.end.tokenize(end)
            lengths.append(tokens.row_lengths())
        else:
            st = examples
        tokens = tokenizers.start.tokenize(st)
        lengths.append(tokens.row_lengths())
    all_lengths = np.concatenate(lengths)

    nearest_pow2 = lambda x: int(2**(np.ceil(np.log2(x))))
    max_length = nearest_pow2(max(all_lengths))

    train_batches = make_transformer_batches(train_examples, 
        tokenizers=tokenizers,
        MAX_TOKENS=max_length)
    val_batches = make_transformer_batches(val_examples, 
        tokenizers=tokenizers,
        MAX_TOKENS=max_length)

    for (st, en), end_labels in train_batches.take(1):
        break

    # create and train the transformer
    num_layers, d_model, dff, num_heads, dropout_rate = default_transformer_params()
    transformer = Transformer(
        num_layers=num_layers,
        d_model=d_model,
        num_heads=num_heads,
        dff=dff,
        input_vocab_size=tokenizers.start.get_vocab_size().numpy(),
        target_vocab_size=tokenizers.end.get_vocab_size().numpy(),
        dropout_rate=dropout_rate)
    
    output = transformer((st, en))
    if debug:
        if debug > 1:
            print(en.shape)
            print(st.shape)
            print(output.shape)

            attn_scores = transformer.decoder.dec_layers[-1].last_attn_scores
            print(attn_scores.shape)  # (batch, heads, target_seq, input_seq)

        print(transformer.summary())

    learning_rate = CustomSchedule(d_model)

    optimizer = tf.keras.optimizers.Adam(
        learning_rate, beta_1=0.88, beta_2=0.975, epsilon=1e-9)

    # # Test the custom learning rate scheduler:
    # if debug > 1:
    #     plt.figure()
    #     plt.plot(learning_rate(tf.range(40000, dtype=tf.float32)))
    #     plt.ylabel('Learning Rate')
    #     plt.xlabel('Train Step')
    #     plt.show()

    # Train the model
    # With all the components ready, configure the training procedure using 
    # model.compile, and then run it with model.fit, this could take a while

    transformer.compile(
        loss=masked_loss,
        optimizer=optimizer,
        metrics=[masked_accuracy])

    transformer.fit(train_batches,
                    epochs=20,
                    validation_data=val_batches)

    if 'transformer_model_name' in yml:
        save_fn = (path.join(yml.primary_path, yml['transformer_model_name']) 
            if (path.sep not in yml['transformer_model_name'])
            else yml['transformer_model_name'])
        tf.saved_model.save(transformer, save_fn)

    translator = Translator(tokenizers, transformer)

    _input = 'Nick Thermopolis; 824 NCR 21G Louisville CO 80412; 7204249201; nick.thermopolis@gmail.com'
    ground_truth = _input

    translated_text, translated_tokens, attention_weights = translator(
        tf.constant(_input))
    
    if debug > 1:
        print_translation(_input, translated_text, ground_truth)

    head = 0
    # Shape: `(batch=1, num_heads, seq_len_q, seq_len_k)`.
    attention_heads = tf.squeeze(attention_weights, 0)
    attention = attention_heads[head]
    attention.shape

    # These are the input tokens:
    in_tokens = tf.convert_to_tensor([_input])
    in_tokens = tokenizers.start.tokenize(in_tokens).to_tensor()
    in_tokens = tokenizers.start.lookup(in_tokens)[0]
    
    
    if __name__ == "__main__":
        test_transformer_embedding_test()