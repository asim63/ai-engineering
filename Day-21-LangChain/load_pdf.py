from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader(r"Day-21-LangChain\sample_pdf.pdf")

docs = loader.load()

print(f"Loaded {len(docs)} pages")
print(docs[1].page_content)