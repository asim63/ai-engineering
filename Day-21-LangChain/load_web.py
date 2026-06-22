from langchain_community.document_loaders import WebBaseLoader

web_loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")
web_docs = web_loader.load()
print(web_docs[0].page_content)