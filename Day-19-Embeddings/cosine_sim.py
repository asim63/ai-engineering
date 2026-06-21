from sentence_transformers import SentenceTransformer
import numpy as np

def cosine_similarity(a,b):
    return np.dot(a,b)/(
        np.linalg.norm(a) * np.linalg.norm(b)
    )   
model = SentenceTransformer("all-MiniLM-L6-v2")
cat = model.encode("The cat is playing on the floor.")
print(cat[:10])
dog = model.encode("The dot is playing on the mat.") 
print(dog[:10])
sky = model.encode("The sky is clear and its sunny.")
print(sky[:10])

cat_cat_cosine = cosine_similarity(cat,cat)
print(cat_cat_cosine)

cat_dog_cosine = cosine_similarity(cat,dog)
print(cat_dog_cosine)

cat_sky_cosine = cosine_similarity(cat,sky)
print(cat_sky_cosine)