from datasets import load_dataset
import json
import os
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone
from pinecone import ServerlessSpec
import time
from tqdm.auto import tqdm
import os
from openai import OpenAI


# Load the secrets from config.json
with open('secrets.json', 'r') as file:
    secrets = json.load(file)

os.environ["OPENAI_API_KEY"] = secrets["OPENAI_API_KEY"]
os.environ["PINECONE_API_KEY"] = secrets["PINECONE_API_KEY"]
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)



dataset = load_dataset("FronkonGames/steam-games-dataset", split="train")
# print(dataset[0])

# Openai embeding dimonsions 1536 for text-embedding-3-small or 3072 for large
embed_model = OpenAIEmbedding(model="text-embedding-3-small", embed_batch_size=128)

# configure client
pc = Pinecone(api_key=secrets["PINECONE_API_KEY"])


spec = ServerlessSpec(
    cloud="aws", region="us-east-1"  # us-east-1
)

dims = len(embed_model.get_text_embedding("some random text blablabla"))
# dims = 1536
# print(dims)

index_name = "ragathon-gpt-4o-research-agent-small"

# check if index already exists (it shouldn't if this is first time)
if index_name not in pc.list_indexes().names():
    # if does not exist, create index
    pc.create_index(
        index_name,
        dimension=dims,  # dimensionality of embed 3
        metric='dotproduct',
        spec=spec
    )
    # wait for index to be initialized
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)

# connect to index
index = pc.Index(index_name)
time.sleep(1)
# view index stats
index.describe_index_stats()

# easier to work with dataset as pandas dataframe
# take first 10k instances as example. Embed more at your convenience
data = dataset.to_pandas().iloc[:1000]
data['AppID'] = data['AppID'].astype(str)
data = data.dropna(subset=['AppID','Release date','Supported languages','Name', 'About the game','Price','User score','Tags'])

batch_size = 128

# ''' data columns name
# AppID,
# Name,
# Release date,
# Estimated owners,
# Peak CCU,
# Required age,
# Price,
# DiscountDLC count,
# About the game,
# Supported languages,
# Full audio languages,
# Reviews,
# Header image,
# Website,
# Support url,
# Support email,
# Windows,
# Mac,
# Linux,
# Metacritic score,
# Metacritic url,
# User score,
# Positive,
# Negative,
# Score rank,
# Achievements,
# Recommendations,
# Notes,
# Average playtime forever,
# Average playtime two weeks,
# Median playtime forever,
# Median playtime two weeks,
# Developers,
# Publishers,
# Categories,
# Genres,
# Tags,
# Screenshots,
# Movies
# '''
'''
for i in tqdm(range(0, len(data), batch_size)):
    i_end = min(len(data), i+batch_size)
    batch = data[i:i_end].to_dict(orient="records")
    # get batch of data
    metadata = [{
        "Name": r["Name"],
        "Price": r["Price"],
        "Release date": r["Release date"],
        "About the game":r["About the game"]
    } for r in batch]
    # generate unique ids for each chunk
    ids = [r["AppID"] for r in batch]
    # get text content to embed
    content = [r["About the game"] for r in batch]
    # embed text
    embeds = embed_model.get_text_embedding_batch(content)
    # add to Pinecone
    vec = zip(ids, embeds, metadata)
    index.upsert(vectors=vec)
'''

query = "i am 21 years old, and I like some adventure games on steam, can you give me some advice"

# create the query vector
limit = 100000
def retrieve(query):
    xq = embed_model.get_text_embedding(query)
    # now query
    res = index.query(vector=xq, top_k=4, include_metadata=True)
    print(res)
    # get relevant contexts
    contexts = []
    contexts = contexts + [
        x['metadata']['Name'] + '. About the ' + x['metadata']['Name']  + ' : '+ x['metadata']['About the game'] for x in res['matches']
    ]
    # build our prompt with the retrieved contexts included
    prompt_start = (
        "Answer the question based on the context below.\n\n"+
        "Context:\n"
    )
    prompt_end = (
        f"\n\nQuestion: {query}\nAnswer:"
    )
    # append contexts until hitting limit
    for i in range(1, len(contexts)):
        if len("\n\n---\n\n".join(contexts[:i])) >= limit:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(contexts[:i-1]) +
                prompt_end
            )
            break
        elif i == len(contexts)-1:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(contexts) +
                prompt_end
            )
    return prompt


def complete(prompt):
    # instructions
    sys_prompt = "You are a helpful assistant that always answers questions."
    # query openai
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
        temperature=0
    )
    return chat_completion.choices[0].message.content


# first we retrieve relevant items from Pinecone
query_with_contexts = retrieve(query)
print(query_with_contexts)
# then we complete the context-infused query
response = complete(query_with_contexts)
print(response)
