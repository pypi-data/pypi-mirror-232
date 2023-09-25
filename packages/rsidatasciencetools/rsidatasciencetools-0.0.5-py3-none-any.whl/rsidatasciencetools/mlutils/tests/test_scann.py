
import h5py
import os
import requests
import tempfile
import time
import numpy as np
from warnings import warn

from rsidatasciencetools.config.baseconfig import EnvConfig

env = EnvConfig(error_no_file_found=False)
# back-up here in case we want to run locally and don't have preset ENV variables
GLOVE_100DIM = env.get('SCANN_TEST_GLOVE_100DIM_URL', "https://ann-benchmarks.com/glove-100-angular.hdf5")  

def test_build_scann_searcher():
    
    try:
        from rsidatasciencetools.mlutils.scann import build_scann_searcher
    except ImportError as ie:
        if 'scann' in str(ie):
            warn(f'could not find "tensorflow" library, skipping test | {str(ie)}')
            return            
        else:
            raise(ie)
    
    with tempfile.TemporaryDirectory() as tmp:
        response = requests.get(GLOVE_100DIM)
        loc = os.path.join(tmp, "glove.hdf5")
        with open(loc, 'wb') as f:
            f.write(response.content)
        
        glove_h5py = h5py.File(loc, "r")
        
    dataset = glove_h5py['train']
    queries = glove_h5py['test']
    print('train:', type(dataset), dataset.shape)
    print('test: ', type(dataset), queries.shape)
    
    # configure ScaNN as a tree - asymmetric hash hybrid with reordering
    # anisotropic quantization as described in the paper; see README
    searcher, _ = build_scann_searcher(dataset, 
        yml=os.path.join(os.path.dirname(__file__),'scann.yml'), debug=1)
    
    def compute_recall(neighbors, true_neighbors):
        total = 0
        for gt_row, row in zip(true_neighbors, neighbors):
            total += np.intersect1d(gt_row, row).shape[0]
        return total / true_neighbors.size
    
    start = time.time()
    neighbors, distances = searcher.search_batched(queries)
    end = time.time()

    # we are given top 100 neighbors in the ground truth, so select top 10
    recall = compute_recall(neighbors, glove_h5py['neighbors'][:, :10])
    rec_str, rec_incorrect, mismatch_neigh = "Recall:", 'computed recall is incorrect', 'mismatched neighbors found'
    print('\nWe are given top 100 neighbors in the ground truth, so select top 10')
    print(rec_str, )
    print("Time:", end - start)
    assert np.isclose(recall,0.9576, atol=3), rec_incorrect
    
    # increasing the leaves to search increases recall at the cost of speed
    start = time.time()
    neighbors, distances = searcher.search_batched(queries, leaves_to_search=150)
    end = time.time()
    print('\nincreasing the leaves to search increases recall at the cost of speed')
    print(rec_str, compute_recall(neighbors, glove_h5py['neighbors'][:, :10]))
    print("Time:", end - start)
    assert np.isclose(recall,0.94014, atol=3), rec_incorrect
    
    # increasing reordering (the exact scoring of top AH candidates) has a similar effect.
    start = time.time()
    neighbors, distances = searcher.search_batched(queries, leaves_to_search=150, pre_reorder_num_neighbors=250)
    end = time.time()
    recall = compute_recall(neighbors, glove_h5py['neighbors'][:, :10])
    print('\nincreasing reordering (the exact scoring of top AH candidates) has a similar effect.')
    print(rec_str, recall)
    print("Time:", end - start)
    assert np.isclose(recall,0.94, atol=3), rec_incorrect
    
    # we can also dynamically configure the number of neighbors returned
    # currently returns 10 as configued in ScannBuilder()
    print('\nwe can also dynamically configure the number of neighbors returned '
        'currently returns 10 as configued in ScannBuilder()')
    neighbors, distances = searcher.search_batched(queries)
    assert(neighbors[:3,].numpy().tolist() == [
        [97478, 846101, 671078, 232287, 727732, 544474, 1133489, 723915, 660281, 566421], 
        [875925, 903728, 144313, 507188, 547349, 643514, 663762, 675600, 891287, 712921], 
        [1046944, 809599, 531832, 323299, 1077727, 704557, 62703, 988527, 377259, 625676]]), (
            mismatch_neigh)
    print(neighbors.shape, distances.shape)

    # now returns 20
    print('now returns 20')
    neighbors, distances = searcher.search_batched(queries, final_num_neighbors=20)
    assert(neighbors[:3,].numpy().tolist() == [
        [97478, 846101, 671078, 232287, 727732, 544474, 1133489, 723915, 660281, 566421, 
            1093917, 908319, 656605, 326455, 1096614, 100206, 547334, 674655, 834699, 445577], 
        [875925, 903728, 144313, 507188, 547349, 643514, 663762, 675600, 891287, 712921, 
            57715, 671097, 188917, 486525, 539829, 732084, 1081448, 246381, 144140, 137766], 
        [1046944, 809599, 531832, 323299, 1077727, 704557, 62703, 988527, 377259, 625676, 
            309652, 569199, 301375, 237710, 859701, 234633, 873673, 599541, 939593, 621820]]), (
            mismatch_neigh)
    print(neighbors.shape, distances.shape)
    
    # we have been exclusively calling batch search so far; the single-query call has the same API
    start = time.time()
    neighbors, distances = searcher.search(queries[0], final_num_neighbors=5)
    end = time.time()
    print('\nwe have been exclusively calling batch search so far; the single-query call has the same API')
    print(distances)
    print("Latency (ms):", 1000*(end - start))
    assert (neighbors[:3,].numpy().tolist() == [97478, 846101, 671078]), (
        mismatch_neigh)
    