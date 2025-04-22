import torch
from sentence_transformers import SentenceTransformer, util

class Fin_Mpnet_Base:
    def __init__(self, model_name: str ='mukaj/fin-mpnet-base', device: str = 'cuda', trust_remote_code: bool = True, documents: list = None):
        self.model = SentenceTransformer(model_name_or_path=model_name, device=device, trust_remote_code=trust_remote_code)

        if documents is not None:
            self.embed_doc(documents)

    def embed_doc(self, documents: list):
        self.documents = self.model.encode(documents)

    def retrieve_relevant_chunk(self, query_list: list, top_k: int = 5):
        query_embeddings = self.model.encode(query_list)
        scores = []
        indices = []
        for query_embedding in query_embeddings:
            cos_scores = util.pytorch_cos_sim(query_embedding, self.documents)[0]
            cos_scores = cos_scores.cpu()
            top_results = torch.topk(cos_scores, k=top_k)
            scores.append(top_results[0].tolist())
            indices.append(top_results[1].tolist())
        return scores, indices

