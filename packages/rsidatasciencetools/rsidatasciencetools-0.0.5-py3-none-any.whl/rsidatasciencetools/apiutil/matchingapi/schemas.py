from pydantic import BaseModel
from typing import List, Dict, Optional


# class DbConfig_t(BaseModel):
#     host: str
#     dialect_driver: str
#     reftable: str
#     port: Optional[int] 
#     user: Optional[str]
#     password: Optional[str]
#     localfile: Optional[bool]
    
# class EmbedConfig_t(BaseModel):
#     merge_fields: List[str]
#     embed_dim: int = 100
#     minn: int = 3
#     embedding_model:str = 'rec_embed'
#     char_ngrams_only:bool = True
    
#     quantize:bool = True
#     scann_num_neighbors: int = 10
#     scann_distance_measure: str = "dot_product"
#     num_leaves: int = None
#     num_leaves_to_search: int = None
#     reordering_num_neighbors: int = None
    
    
# class SetConfig_t(BaseModel):
#     tenant: str
#     dbconfig: DbConfig_t
#     embed_config: EmbedConfig_t
    
class SetConfig_t(BaseModel):
    # tenant: str
    dbconfig: Dict
    embed_config: Dict
