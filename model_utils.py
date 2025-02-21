import numpy as np
import tensorflow as tf
from tensorflow import keras
import json
from json import JSONEncoder

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

def save_model_json(model, layers_to_skip=(keras.layers.InputLayer), skip=0, samplerate=48000.0, author="Unknown", esr=0.99):
    def get_layer_type(layer):
        if isinstance(layer, keras.layers.TimeDistributed):
            return 'time-distributed-dense'

        if isinstance(layer, keras.layers.GRU):
            return 'gru'

        if isinstance(layer, keras.layers.LSTM):
            return 'lstm'

        if isinstance(layer, keras.layers.Dense):
            return 'dense'

        if isinstance(layer, keras.layers.Conv1D):
            return 'conv1d'

        return 'unknown'

    def get_layer_activation(layer):
        if not hasattr(layer, 'activation'):
            return ''

        if isinstance(layer, keras.layers.TimeDistributed):
            return get_layer_activation(layer.layer)

        if layer.activation == keras.activations.tanh:
            return 'tanh'

        if layer.activation == keras.activations.relu:
            return 'relu'

        if layer.activation == keras.activations.sigmoid:
            return 'sigmoid'

        if layer.activation == keras.activations.softmax:
            return 'softmax'

        if layer.activation == keras.activations.elu:
            return 'elu'
        
        return ''

    def save_layer(layer):
        layer_dict = {
            "type"       : get_layer_type(layer),
            "activation" : get_layer_activation(layer),
            "shape"      : layer.output_shape,
            "weights"    : layer.get_weights()
        }

        if layer_dict["type"] == "conv1d":
            layer_dict["kernel_size"] = layer.kernel_size
            layer_dict["dilation"] = layer.dilation_rate

        return layer_dict

    model_dict = {}
    model_dict["in_shape"] = model.input_shape

    # This parameter in Automated-GuitarAmpModelling indicates
    # how many elements of the input vector has been skipped, aka reported
    # directly to the output during training. If skip=1, y[n] = network.forward(x[n]) + x[n].
    if skip > 0:
        model_dict["in_skip"] = skip

    layers = []
    for layer in model.layers:
        if isinstance(layer, layers_to_skip):
            print(f'Skipping layer: {layer}')
            continue
        else:
            print(f'Processing layer: {layer}')
            layer_dict = save_layer(layer)
            layers.append(layer_dict)

    model_dict["layers"] = layers
    model_dict["samplerate"] = samplerate
    model_dict["author"] = author
    model_dict["esr"] = esr
    return model_dict

def save_model(model, filename, layers_to_skip=(keras.layers.InputLayer), skip=0, samplerate=48000.0, author="Unknown", esr=0.99):
    model_dict = save_model_json(model, layers_to_skip, skip, samplerate, author, esr)
    with open(filename, 'w') as outfile:
        json.dump(model_dict, outfile, cls=NumpyArrayEncoder, indent=4)
