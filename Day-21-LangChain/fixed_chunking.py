from langchain_text_splitters import CharacterTextSplitter
import re

def clean_text(text):
    text = re.sub(r'\n+','\n',text) #removes newlines
    text = re.sub(r'\s+',' ',text) # removes repeated whitespace
    text = re.sub(r"Page \d+","", text) #removes page numbers.
    return text.strip()


sample_text = """I am Asim currently doing bachelors of computer engineering. 


Along with my engineering, i have recently been doing LSPP 60 days challenge where 

i have been learning AI engineering. Its really
fun and it kinda makes your habit into doing and learning something new  
each day. I have just stated learning RAG, 
and today i am learning document loading(one of the    first
steps in RAG pipeline)."""


cleaned_text = clean_text(sample_text)
# print(clean_text(sample_text))

fixed_splitter = CharacterTextSplitter(
    separator=" ",
    chunk_size = 100,
    chunk_overlap = 10
)
fixed_chunks = fixed_splitter.split_text(cleaned_text)

for i, chunk in enumerate(fixed_chunks):
    print(f"\nChunk {i+1}:")
    print(chunk)