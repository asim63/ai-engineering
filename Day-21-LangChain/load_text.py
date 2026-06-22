from langchain_community.document_loaders import TextLoader

loader = TextLoader(r"Day-21-LangChain\text.txt")
docs = loader.load()
print(docs[0].metadata)
