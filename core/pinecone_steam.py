from datasets import load_dataset
import json
import os
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone
from pinecone import ServerlessSpec
import time
from tqdm.auto import tqdm

# Load the secrets from config.json
with open('secrets.json', 'r') as file:
    secrets = json.load(file)

os.environ["OPENAI_API_KEY"] = secrets["OPENAI_API_KEY"]
os.environ["PINECONE_API_KEY"] = secrets["PINECONE_API_KEY"]


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

index_name = "gpt-4o-research-agent"

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
data = dataset.to_pandas().iloc[:10000]
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
for i in tqdm(range(0, len(data), batch_size)):
    i_end = min(len(data), i+batch_size)
    batch = data[i:i_end].to_dict(orient="records")
    # get batch of data

    metadata = [{
        "Name": r["Name"],
        "Price": r["Price"],
        "Release date": r["Release date"],
        "User score": r["User score"],
        "Tags": r["Tags"],
        "Supported languages": r["Supported languages"]
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