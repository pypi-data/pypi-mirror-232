'''tensorflow utilities'''

import tensorflow as tf


def wrap_and_save_tf_model(model):
    class NLPmodel(tf.Module):
        def __init__(self, model):
            self.model = model

        @tf.function(input_signature=[tf.TensorSpec(shape=[], dtype=tf.string)])
        def __call__(self, sentence):
            (result,
            tokens,
            attention_weights) = self.model(sentence, max_length=64)

            return result
    tf_model = NLPmodel(model)
    tf.saved_model.save(tf_model, export_dir='translator')

def save_tf_dataset(dataset, location='data/tf-records/'):
    dataset = dataset.map(tf.io.serialize_tensor)
    writer = tf.data.experimental.TFRecordWriter(location)
    writer.write(dataset)
    return location


# def load_tf_dataset(tf_record, types=tf.string):
#     dataset = tf.data.TFRecordDataset(tf_record)

#     features={
#         'text': tf.io.FixedLenFeature([], tf.string, default_value=''),
#     }
#     def parser(example):
#         parsed_feat = tf.io.parse_single_example(example, features)
#         # text = tf.io.decode_raw(parsed_feat['text'], tf.string)
#         return parsed_feat['text'], None
#         # return text, None
#     # parser = tf.io.FixedLenSequenceFeature((None,), 
#     #     dtype=tf.string, allow_missing=True, default_value='')
#     dataset = dataset.map(lambda x: 
#         # tf.io.parse_tensor(x, types)
#         parser(x)[0]
#         )
#     return dataset

potential_layers = [
    'encoder', 'decoder', 'final_layer', 'layers',
    'self_attention', 'causal_self_attention', 
    'cross_attention', 'ffn', 'mha', 
    'pos_embedding', 'embedding']
check_layers = lambda x: any(hasattr(x,k) for k in potential_layers)


def reset_transformer_weights(model, layerstack=None, session=None, simple_tf=True, debug=0):
    K = None
    if session is None:
        import keras.backend as K
        session = K.get_session()
    if simple_tf:
        if K is None:
            import keras.backend as K
        session.close()
        K.set_session(tf.Session())
        session = K.get_session()
        session.run(tf.global_variables_initializer())
    else:
        layerstack = ("" if layerstack is None else layerstack + ".") + model.__class__.__name__
        if hasattr(model,'layers'):
            for ll, layer in enumerate(model.layers):
                init_layer(getattr(model,attr), 
                    layerstack=layerstack + "." + layer.__class__.__name__ + f'.L[{ll}]', 
                    session=session, debug=debug)
                if check_layers(layer):
                    # call the next layer deep
                    reset_transformer_weights(layer, layerstack=layerstack, session=session, 
                        simple_tf=False, debug=debug)

        for attr in potential_layers:
            if attr == 'layers':
                continue
            if hasattr(model, attr):
                layer = getattr(model,attr)
                init_layer(layer, layerstack=layerstack + "." + layer.__class__.__name__, 
                    session=session, debug=debug)
                if check_layers(layer):
                    # call the next layer deep
                    reset_transformer_weights(layer, layerstack=layerstack, session=session, 
                        simple_tf=False, debug=debug)

def init_layer(layer, layerstack, session, debug=0):
    for el, el_name in zip(['kernel_initializer', '_kernel_initializer', 
                        'bias_initializer', '_bias_initializer'],[
                        'kernel', 'kernel', 'bias', 'bias']):
        if hasattr(layer, el): 
            debug and print(f'{layerstack}: initializing {el_name} weights')
            # if el.startswith('_'):
            #     getattr(layer,el).run(session=session)
            # else:
            getattr(layer,el_name).initializer.run(session=session)