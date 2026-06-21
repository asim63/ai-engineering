from chroma_class import DocumentStore

doc = DocumentStore()

doc.add_document(document="AI engineering is cool.",ids = "1",metadata= {"category":"ai"})
doc.add_document(document="I love to listen to music",ids = "2",metadata= {"category":"music"})
doc.add_document(document="Momos are really delicious.",ids = "3",metadata= {"category":"food"})


result = doc.search(query = "I am really bored.")
print(result)