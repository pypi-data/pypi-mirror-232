'''shortcut init function for creating a SCANN fast quantized MIP embedding query object'''
'''
ScaNN (Scalable Nearest Neighbors) is a method for efficient vector similarity
search at scale. This code release implements [1], which includes search space
pruning and quantization for Maximum Inner Product Search and also supports
other distance functions such as Euclidean distance. The implementation is
designed for x86 processors with AVX2 support. ScaNN achieves state-of-the-art
performance on [ann-benchmarks.com](http://ann-benchmarks.com) as shown on the
glove-100-angular dataset below:

![glove-100-angular](https://github.com/google-research/google-research/raw/master/scann/docs/glove_bench.png)

ScaNN can be configured to fit datasets with different sizes and distributions.
It has both TensorFlow and Python APIs. The library shows strong performance
with large datasets [1]. The code is released for research purposes. For more
details on the academic description of algorithms, please see [1].

Reference [1]:
```
@inproceedings{avq_2020,
  title={Accelerating Large-Scale Inference with Anisotropic Vector Quantization},
  author={Guo, Ruiqi and Sun, Philip and Lindgren, Erik and Geng, Quan and Simcha, 
    David and Chern, Felix and Kumar, Sanjiv},
  booktitle={International Conference on Machine Learning},
  year={2020},
  URL={https://arxiv.org/abs/1908.10396}
}
```

To get this to run locally please run the following steps 
(see .github/workflows/build.yml):
    - name: Install bazel build system
    - name: Install pybind11, numpy, tf, and pytest modules
    - name: Install the google 'scann' module

The dependencies are difficult to get correct, so some external help has been useful:
https://eugeneyan.com/writing/how-to-install-scann-on-mac/

See also the ScaNN [README](https://github.com/google-research/google-research/blob/master/scann/README.md) 
for the above details and more.

For parameter settings, see
https://github.com/google-research/google-research/blob/master/scann/docs/algorithms.md

the `training_sample_size` in particular doesn't seem to have any clear rules; see
https://github.com/google-research/google-research/issues/622
'''
import numpy as np
from warnings import warn

from rsidatasciencetools.config.baseconfig import YmlConfig

from scann.scann_ops.py.scann_builder import ScannBuilder
from scann.scann_ops.py.scann_ops import ScannSearcher, scann_create_searcher


# populate defaults if parameter not present in yml settings and 
# auto-select use of partitioning and reordering according to the 
# guidelines layed out in: 
# https://github.com/google-research/google-research/blob/master/scann/docs/algorithms.md
scann_defaults = dict(
    num_neighbors=10, 
    distance_measure="dot_product",
    
    num_leaves=lambda N, M: 2 * int(np.sqrt(N)), 
    num_leaves_to_search=lambda N, M: int(max(np.sqrt(N)/5, 4 * M)), 
    reordering_num_neighbors=lambda N, M: int(max(np.sqrt(N)/4, 8 * M)),

    use_partitioning_asymhash=lambda N, M: (N >= 20e3),

    training_sample_size=lambda N, M: N,
    
    dimensions_per_block=2, 
    anisotropic_quantization_threshold=0.2
)


def update_scann_params(yml, N, debug=0):
    '''
    populate defaults if parameter not present in yml settings 
    '''
    for k in scann_defaults:
        default = (scann_defaults[k](
            N,yml.get('num_neighbors', scann_defaults['num_neighbors'])) 
            if callable(scann_defaults[k]) else scann_defaults[k])
        yml.setkeyvalue(k,yml.get(k, default))
    
    debug and print(yml)    
    return yml


def build_scann_searcher(dataset, yml={}, debug=0):
    ''' Build a 'scann'  search object for doing fast matching 
        of embeddings via minimum inner-product and anisotropic 
        quantization  
    '''
    if not isinstance(yml, YmlConfig):
        yml = YmlConfig(yml, error_no_file_found=False)
    normalized_dataset = dataset / np.linalg.norm(dataset, 
        axis=1)[:, np.newaxis]
    N = normalized_dataset.shape[0]
    yml = update_scann_params(yml,N,debug=debug)
    
    # use scann.scann_ops.build() to instead create a TensorFlow-compatible searcher
    def builder_lambda(db, config, training_threads, **kwargs):
        return scann_create_searcher(db, config, training_threads, **kwargs)

    if yml['use_partitioning_asymhash']:
        # configure ScaNN as a tree - asymmetric hash hybrid with reordering
        
        if N >= 100e3:
            searcher = ScannBuilder(
                    normalized_dataset, yml['num_neighbors'], yml['distance_measure']
                ).tree(
                    num_leaves=yml['num_leaves'], 
                    num_leaves_to_search=yml['num_leaves_to_search'], 
                    training_sample_size=yml['training_sample_size']
                ).score_ah(
                    dimensions_per_block=yml['dimensions_per_block'], 
                    anisotropic_quantization_threshold=yml['anisotropic_quantization_threshold']
                ).reorder(
                    reordering_num_neighbors=yml['reordering_num_neighbors']
                ).set_builder_lambda(builder_lambda).build()
        else:
            searcher = ScannBuilder(
                    normalized_dataset, yml['num_neighbors'], yml['distance_measure']
                ).score_ah(
                    dimensions_per_block=yml['dimensions_per_block'], 
                    anisotropic_quantization_threshold=yml['anisotropic_quantization_threshold']
                ).reorder(
                    reordering_num_neighbors=yml['reordering_num_neighbors']
                ).set_builder_lambda(builder_lambda).build()
    else: 
        # configure ScaNN using brute-force search
        if N > 20e3:
            warn('specifying brute-force look up (no hashing or paritioning), but '
                'this is a large dataset, results will be quite slow')
        searcher = ScannBuilder(normalized_dataset, 
            yml['num_neighbors'], yml['distance_measure']).score_brute_force(
                quantize=True).set_builder_lambda(builder_lambda).build()
    
    return ScannSearcher(searcher), yml
    