import chromadb

class DocumentStore():
    
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name = "document")
        
    def add_document(self,document,ids,metadata = None):
        self.collection.add(
            documents= [document],
            ids = [ids],
            metadatas=[metadata] if metadata else None
        )
    def search(self,query,metadata_filter=None, n_results = 3):
        return self.collection.query(
            query_texts= query,
            where = metadata_filter,
            n_results= n_results
        )
    def delete_document(self,doc_id):
        self.collection.delete(ids=[doc_id])