import json
import openai
from pymongo import MongoClient
import urllib.parse
from tabulate import tabulate
import pandas as pd
import os
from dotenv import load_dotenv


load_dotenv() 

openai.api_key = os.getenv('OPENAI_API_KEY')

# MongoDB credentials
username = urllib.parse.quote_plus(os.getenv('MONGO_USERNAME'))
password = urllib.parse.quote_plus(os.getenv('MONGO_PASSWORD'))

# Construct the MongoDB URI
uri = f"mongodb+srv://{username}:{password}@atlascluster.o3j64gg.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"
client = MongoClient(uri)
db = client[os.getenv('MONGO_DATABASE')]


# Function to generate a query using OpenAI
def generate_mongodb_query(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7
    )
    return response.choices[0].message['content'].strip()



def getDataUsingQuery(collection, query):
    data = list(collection.find({}, {'_id': 0}).limit(2))
    data_json = json.dumps(data, indent=4)
    
    prompt = f"""
            Given the following JSON data:
            {data_json}
            Generate only the query in JSON format without any extra text:

            {query}
            """
    result = generate_mongodb_query(prompt)    
    clean_result = result.replace('```json', '').replace('```', '').strip()

    clean_result_query = json.loads(clean_result)
    output_data = list(collection.find(clean_result_query, {'_id': 0}))
    
    return output_data
    
            
            

def getDataForModels(query):
    collection = db[os.getenv('MODELS_COLLECTION')]
    result = getDataUsingQuery(collection, query)
    return result
    
def getDataForConfluencePages(query):
    collection = db[os.getenv('CONFLUENCE_COLLECTION')]
    result = getDataUsingQuery(collection, query)
    return result


if __name__ == "__main__":
    query = input('Enter your Query ')
    result = getDataForModels(query)
    print(result)
    
    
    # getDataForConfluencePages(query)
    
    # # Convert the result json data to a DataFrame
    # df_active_data = pd.DataFrame(result)
    # print(tabulate(df_active_data, headers='keys', tablefmt='psql'))
    
