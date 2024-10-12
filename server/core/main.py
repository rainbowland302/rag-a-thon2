from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import os
import json

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load the secrets from config.json
secrets_path = os.path.join(current_dir, 'secrets.json')
with open(secrets_path, 'r') as file:
    secrets = json.load(file)

os.environ["OPENAI_API_KEY"] = secrets["OPENAI_API_KEY"]

# Load documents and create index (do this once at startup)
data_path = os.path.join(current_dir, 'data')
documents = SimpleDirectoryReader(data_path).load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

def get_response(query):
    response = query_engine.query(query)
    # Convert response to string for easy JSON serialization
    return str(response)

if __name__ == '__main__':
    # Example usage
    print(get_response(
        'I like playing strategy games. Can you recommend some strategy games published on Steam in 2024?'))
