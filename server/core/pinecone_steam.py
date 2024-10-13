from datasets import load_dataset
import os
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone
from pinecone import ServerlessSpec
import time
from tqdm.auto import tqdm
from openai import OpenAI
from dotenv import load_dotenv

# from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
# from phoenix.otel import register
#
#
# tracer_provider = register(
#     project_name="immerse-into-real-steam-games",  # Default is 'default'
#     endpoint="http://localhost:6006/v1/traces",
# )
#
# LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
server_dir = os.path.dirname(current_dir)

# Load environment variables from .env file
load_dotenv(os.path.join(server_dir, '.env'))

# Now you can access the environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
together_api_key = os.getenv("TOGETHER_API_KEY")
replicate_api_token = os.getenv("REPLICATE_API_TOKEN")


client = OpenAI(
    api_key=openai_api_key,
)

dataset = load_dataset("FronkonGames/steam-games-dataset", split="train")
# print(dataset[0])

# Openai embeding dimonsions 1536 for text-embedding-3-small or 3072 for large
embed_model = OpenAIEmbedding(model="text-embedding-3-small", embed_batch_size=128)

# configure client
pc = Pinecone(api_key=pinecone_api_key)

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
data = data.dropna(
    subset=['AppID', 'Release date', 'Supported languages', 'Name', 'About the game', 'Price', 'User score', 'Tags'])

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
        x['metadata']['Name'] + '. About the ' + x['metadata']['Name'] + ' : ' + x['metadata']['About the game'] for x
        in res['matches']
    ]
    # build our prompt with the retrieved contexts included
    prompt_start = (
            "Answer the question based on the context below.\n\n" +
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
                    "\n\n---\n\n".join(contexts[:i - 1]) +
                    prompt_end
            )
            break
        elif i == len(contexts) - 1:
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

import os
import asyncio
# from llama_index.utils.workflow import draw_all_possible_flows

from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Event,
)

from dotenv import load_dotenv
load_dotenv()


class FirstEvent(Event):
    first_output: str


class ImageGenerator(Workflow):
    @step()
    async def generate(self, ev: StartEvent) -> FirstEvent:
        from llama_index.llms.openai import OpenAI
        query = ev.first_input
        print(query)
        llm = OpenAI()
        response = await llm.acomplete(query)
        return FirstEvent(first_output=str(response))

    @step()
    async def generate_image(self, ev: FirstEvent) -> StopEvent:
        query = ev.first_output
        print(query)
        from openai import OpenAI
        client = OpenAI(
            api_key=together_api_key, base_url="https://api.together.xyz/v1"
        )
        response = client.images.generate(
            prompt=query,
            model="black-forest-labs/FLUX.1.1-pro",
            n=1,
        )
        print(response.data[0].url)
        return StopEvent(result=str(response.data[0].url))



import replicate
import asyncio

from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Event,
)

from dotenv import load_dotenv
load_dotenv()

class FirstMusicEvent(Event):
    first_output: str

class MusicGenerator(Workflow):
    @step()
    async def generate(self, ev: StartEvent) -> FirstMusicEvent:
        query = ev.first_input

        from openai import OpenAI
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        result_music_prompt = completion.choices[0].message

        return FirstMusicEvent(first_output=str(result_music_prompt))

    @step()
    async def generate_music(self, ev: FirstMusicEvent) -> StopEvent:
        query = ev.first_output
        print(os.environ.get(''))
        print(query)
        input = {
            "prompt": query,
            "model_version": "stereo-large",
            "output_format": "mp3",
            "normalization_strategy": "peak"
        }

        output = replicate.run(
            "meta/musicgen:671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedcfb",
            input=input
        )
        # print(output)
        return StopEvent(result=str(output))



def get_response(query):
    # query = "i am 21 years old, and I like some adventure games on steam, can you give me some advice"
    query_with_contexts = retrieve(query)
    # print(query_with_contexts)
    # then we complete the context-infused query
    response = complete(query_with_contexts)
    # return str(response)


    #run music generation firt
    # user_in = "I want to play a popular casual game, do you have any recommendations"
    prompt = "Help me change this sentence into a prompt suitable for generating music. "
    query_with_prompt = query + prompt
    print(query_with_prompt)

    async def musicgen():
        w = MusicGenerator(timeout=30000, verbose=False)
        print('bugs here?: ' + query_with_prompt)
        url = await w.run(
            first_input=query_with_prompt)
        return url

    music_url = asyncio.run(musicgen())
    # draw_all_possible_flows(ImageGenerator, filename="image_generator_step_workflow.html")


    async def imagegen():
        w = ImageGenerator(timeout=30000, verbose=False)
        url = await w.run(
            first_input="help me write a prompt for image generation, I want a photo of the recommended games" + str(response))
        return url

    url_flux = asyncio.run(imagegen())
    # draw_all_possible_flows(ImageGenerator, filename="image_generator_step_workflow.html")
    res = {
        "res": str(response),
        "img": str(url_flux),
        "aud": str(music_url)
    }
    return res

