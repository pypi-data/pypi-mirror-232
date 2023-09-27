import requests
import json
from urllib.parse import quote
import os
# from embeddings.embeddings import Embeddings

from sys import exit
import faiss
import tiktoken
import numpy as np
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from langchain.docstore.in_memory import InMemoryDocstore


from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from typing import Any, Callable, Dict, List, Optional, Union

# from utils.utils import Utils
# from loaders.berrydb_json_loader import BerryDBJSONLoader
# from berrydb_json_csv_loader import BerryDBJSONCSVLoader


debug_mode = True

base_url = "https://app.berrydb.io"
berry_gpt_base_url = "http://gpt.berrydb.io:9090"

get_database_id_url = base_url + "/profile/database"
get_database_list_by_api_key_url = base_url + "/profile/database/list-by-api-key"

documents_url = base_url + "/berrydb/documents"
query_url = base_url + "/berrydb/query"
document_by_id_url = base_url + "/berrydb/documents/{}"
bulk_upsert_documents_url = base_url + "/berrydb/documents/bulk"

transcription_url = berry_gpt_base_url + "/transcription"
caption_url = berry_gpt_base_url + "/caption"


class BerryDB:
    @classmethod
    def connect(self, api_key: str, database_name: str, bucket_name: str):
        """Function summary

        Args:
            arg1 (str): API Key
            arg2 (str): Database Name
            arg3 (str): Bucket Name

        Returns:
            Database Reference: An instance of the database
        """

        if debug_mode:
            print("api_key: ", api_key)
            print("database_name: ", database_name)
            print("bucket_name: ", bucket_name)
            print("\n\n")

        database_id: int = self.__getDataBaseId(self, api_key, database_name)

        return Database(api_key, bucket_name, database_id, database_name)

    @classmethod
    def databases(self, api_key: str):
        """Function summary

        Args:
            arg1 (str): API Key

        Returns:
            list: Dict of Databases
        """

        url = get_database_list_by_api_key_url
        params = {"apiKey": api_key}

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            jsonResponse = response.json()
            if debug_mode:
                print("databases result ", jsonResponse)
            if (
                "database" in jsonResponse
                and "responseList" in jsonResponse["database"]
            ):
                databaseNames = {}
                # print("\nDatabases:")
                for db in jsonResponse["database"]["responseList"]:
                    name = db["name"] if db["name"] else ""
                    schemaName = db["schemaName"] if db["schemaName"] else ""
                    description = db["description"] if db["description"] else ""
                    dbId = db["id"] if db["id"] else ""
                    schemaId = db["schemaId"] if db["schemaId"] else ""
                    databaseNames[name] = {
                        "id": dbId,
                        "schemaId": schemaId,
                        "schemaName": schemaName,
                        "description": description,
                    }
                    # print(name + " : " + str(databaseNames[name]))
                # print("\n")
                return databaseNames
            return {}
        except Exception as e:
            print("Failed to fetch databases: {}".format(str(e)))
            return {}

    def __getDataBaseId(self, api_key: str, database_name: str) -> int:
        """Function summary

        Args:
            arg1 (str): API Key
            arg2 (str): Database Name

        Returns:
            int : Database ID
        """

        url = get_database_id_url
        params = {"apiKey": api_key, "databaseName": database_name}

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(self, response.json(), response.status_code)
            if debug_mode:
                print("documents result ", response.json())
            json_res = json.loads(response.text)
            if json_res.get("database", None):
                return json_res["database"].get("id", None)
            return
        except Exception as e:
            print("Failed to fetch your database: {}".format(str(e)))
            return None


class Database:
    __api_key: str
    __bucket_name: str
    __database_id: int
    __database_name: str

    def __init__(
        self, api_key: str, bucket_name: str, database_id: int, database_name: str
    ):
        if api_key is None:
            Utils.print_error_and_exit("API Key cannot be None")
        if bucket_name is None:
            Utils.print_error_and_exit("Bucket name cannot be None")
        if database_id is None:
            Utils.print_error_and_exit("Database not found")
        self.__api_key = api_key
        self.__bucket_name = bucket_name
        self.__database_id = database_id
        self.__database_name = database_name

    def apiKey(self):
        return self.__api_key

    def bucketName(self):
        return self.__bucket_name

    def databaseId(self):
        return self.__database_id

    def databaseName(self):
        return self.__database_name

    def get_all_documents(self):
        """Function summary

        Args:
            No Arguments

        Returns:
            list: List of Documents
        """

        url = documents_url
        params = {
            "apiKey": self.__api_key,
            "bucket": self.__bucket_name,
            "databaseId": self.__database_id,
        }

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("documents result ", response.json())
            return json.loads(response.text)
        except Exception as e:
            print("Failed to fetch document: {}".format(str(e)))
            return []

    def get_all_documents_with_col_filter(self, col_filter=["*"]):
        """Function summary

        Args:
            arg1 (list<str>): Column list (Optional)

        Returns:
            list: List of Documents
        """

        url = documents_url
        """ params = {
            "columns": col_filter,
            "apiKey": self.__api_key,
            "bucket": self.__bucket_name,
            "databaseId": self.__database_id,
        } """
        url += "?apiKey=" + self.__api_key
        url += "&bucket=" + self.__bucket_name
        url += "&databaseId=" + str(self.__database_id)
        url += "&columns=" + (",".join(col_filter))

        if debug_mode:
            print("url:", url)
        try:
            response = requests.get(url)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("documents result ", response.json())
            # return response.json()
            return json.loads(response.text)
        except Exception as e:
            print("Failed to fetch document: {}".format(str(e)))
            return []

    def get_document_by_object_id(
        self,
        document_id,
        key_name=None,
        key_value=None,
    ):
        """Function summary

        Args:
            arg1 (str): Document Key/Id
            arg2 (str): Key Name (optional)
            arg3 (str): Key Value (optional)

        Returns:
            list: List of Documents
        """

        url = document_by_id_url.format(quote(document_id))
        params = {
            "apiKey": self.__api_key,
            "bucket": self.__bucket_name,
            "databaseId": self.__database_id,
        }

        if document_id is not None:
            params["docId"] = document_id
        if key_name is not None:
            params["keyName"] = key_name
        if key_value is not None:
            params["keyValue"] = key_value

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            jsonRes = response.json()
            if debug_mode:
                print("docById result ", jsonRes)
            return jsonRes
        except Exception as e:
            print("Failed to fetch document by id {} : {}".format(document_id, str(e)))
            return ""

    def query(self, query: str):
        """Function summary

        Args:
            arg1 (str): Query String

        Returns:
            list: List of Documents
        """

        url = query_url
        params = {
            "apiKey": self.__api_key,
            "bucket": self.__bucket_name,
            "databaseId": self.__database_id,
        }
        payload = query

        if debug_mode:
            print("url:", url)
            print("query:", query)
            print("params:", params)
        headers = Utils.get_headers(self.__api_key)

        try:
            response = requests.post(url, data=payload, headers=headers, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("query result ", response.json())
            return json.loads(response.text)
        except Exception as e:
            print("Failed to query : {}".format(str(e)))
            return ""

    def __upsert(self, documents) -> str:
        url = bulk_upsert_documents_url
        params = {
            "apiKey": self.__api_key,
            "bucket": self.__bucket_name,
            "databaseId": self.__database_id,
        }

        payload = json.dumps(documents)
        if debug_mode:
            print("url:", url)
            print("payload:", payload)
        headers = Utils.get_headers(self.__api_key)

        try:
            response = requests.post(url, data=payload, headers=headers, params=params)
            if response.status_code != 200:
                try:
                    resp_content = response.json()
                except ValueError:
                    resp_content = response.text
                Utils.handleApiCallFailure(resp_content, response.status_code)
            if debug_mode:
                print("upsert result ", response)
            return response.text
        except Exception as e:
            print("Failed to upsert document: {}".format(str(e)))
            return ""

    def upsert(self, documents) -> str:
        """Function summary

        Args:
            arg1 (str): List of documents Object to add/update (Each document should have a key 'id' else a random string is assigned)

        Returns:
            str: Success/Failure message
        """
        return self.upsert_document(documents)

    def upsert_document(self, documents) -> str:
        """Function summary

        Args:
            arg1 (str): List of documents Object to add/update (Each document should have a key 'id' else a random string is assigned)

        Returns:
            str:  Success/Failure message
        """

        try:
            if type(documents) != list:
                documents = [documents]
            return self.__upsert(documents)
        except Exception as e:
            print("Failed to upsert documents: {}".format(str(e)))
            return ""

    def deleteDocument(self, document_id):
        """Function summary

        Args:
            arg1 (str): Document Data Object to delete a document by id

        Returns:
            str: Success message
        """

        url = document_by_id_url.format(quote(document_id))
        params = {
            "apiKey": self.__api_key,
            "bucket": self.__bucket_name,
            "databaseId": self.__database_id,
        }

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.delete(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            jsonRes = response.text
            if debug_mode:
                print("Delete document result ", jsonRes)
            return jsonRes
        except Exception as e:
            print(
                "Failed to delete document by id {}, reason : {}".format(
                    document_id, str(e)
                )
            )
            return ""

    def transcribe(self, video_url: str):
      url = transcription_url

      body = {
        "url": video_url,
      }

      payload = json.dumps(body)
      if debug_mode:
          print("url:", url)
          print("payload:", payload)
      headers = Utils.get_headers(self.__api_key)

      try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code != 200:
          Utils.handleApiCallFailure(response.json(), response.status_code)
        res = response.text
        if debug_mode:
          print("Transcription result: ", res)
        return res
      except Exception as e:
        print(f"Failed to get transcription for the url {video_url}, reason : {str(e)}")
        return ""

    def caption(self, image_url: str):
      url = caption_url

      body = {
        "url": image_url,
      }

      payload = json.dumps(body)
      if debug_mode:
        print("url:", url)
        print("payload:", payload)
      headers = Utils.get_headers(self.__api_key)

      try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code != 200:
          Utils.handleApiCallFailure(response.json(), response.status_code)
        res = response.text
        if debug_mode:
          print("Caption result: ", res)
        return res
      except Exception as e:
        print(f"Failed to get caption for the url {image_url}, reason : {str(e)}")
        return ""

    def embed(self, open_ai_api_key, embedding_function = None, limit = None):
        """Function summary

        Args:
            arg1 (str): OpenAI API key to embed the database

        Returns:
            str: An instance of the Embeddings class
        """

        embeddings = Embeddings(
          self.__database_id,
          self.__bucket_name,
          self.__bucket_name,
          self.__api_key,
          open_ai_api_key,
          embedding_function,
          limit
        )
        return embeddings

class Embeddings:
  __berry_db_api_key: str
  __open_ai_api_key: str
  __bucket_name: str
  __database_id: str
  __database_name: str
  __embedding_function: str
  __limit: str

  def __init__(
    self,
    database_id: int,
    database_name: str,
    bucket_name: str,
    berry_db_api_key: str,
    open_ai_api_key: str,
    limit: int = None,
    embedding_function = None,
  ):
      if not database_id:
        Utils.print_error_and_exit("Database cannot be None")
      if not database_name:
        Utils.print_error_and_exit("Database name cannot be None")
      if not bucket_name:
        Utils.print_error_and_exit("Bucket name cannot be None")
      if not berry_db_api_key:
        Utils.print_error_and_exit("API Key cannot be None")
      if not open_ai_api_key:
        Utils.print_error_and_exit("OpenAI API Key cannot be None")
      if limit and (type(limit) != 'int' and int(limit) > 0):
        Utils.print_error_and_exit("Limit should be none or a positive integer")

      self.__berry_db_api_key = berry_db_api_key
      self.__open_ai_api_key = open_ai_api_key
      self.__bucket_name = bucket_name
      self.__database_id = database_id
      self.__database_name = database_name
      self.__embedding_function = embedding_function
      self.__limit = int(limit) if limit else None


  # @classmethod
  def embedDb(self):

      if not self.__database_id:
        Utils.print_error_and_exit("Database cannot be None")
      if not self.__database_name:
        Utils.print_error_and_exit("Database name cannot be None")
      if not self.__bucket_name:
        Utils.print_error_and_exit("Bucket name cannot be None")
      if not self.__berry_db_api_key:
        Utils.print_error_and_exit("API Key cannot be None")
      if not self.__open_ai_api_key:
        Utils.print_error_and_exit("OpenAI API Key cannot be None")
      if self.__limit and (type(self.__limit) != 'int' and int(self.__limit) > 0):
        Utils.print_error_and_exit("Limit should be none or a positive integer")

      if debug_mode:
        print("self.__database_id: ", self.__database_id)
        print("self.__database_name: ", self.__database_name)
        print("self.__bucket_name: ", self.__bucket_name)

      documents = []
      print(f"Checking if you have access to {self.__database_name}")
      records = self.__get_all_records_for_database()
      records = [item["BerryDb"] for item in records]
      if self.__limit:
        records = records[: self.__limit]
      print(f"Fetched {len(records)} records")
      if len(records) <= 0:
        """raise HTTPException(
            status_code=400, detail="Database does not have any records"
        )"""
        Utils.print_error_and_exit("Database does not have any records")


      documents = self.__load_JSON(records)

      tokens, embedding_cost = self.__calculate_embedding_cost(documents)
      print(f'Embedding Cost: ${embedding_cost:.4f}')
      print(f'Number of chunks: {len(documents)}')

      return self.__embed_docs(documents, True, self.__embedding_function)

  def __get_embeddings_from_docs(self, texts, open_ai_api_key):
    return OpenAIEmbeddings(openai_api_key=open_ai_api_key)

  def __get_vector_store(self):
    if not self.is_embedded():
      Utils.print_error_and_exit(f"Database with name {self.__database_name} is not embedded. Please embed the database and try again.")
    records = self.__get_all_records_for_database()
    records = [item["BerryDb"] for item in records]
    docs = self.__load_JSON(records)
    vector_store = self.__embed_docs(docs)
    return vector_store

  def __embed_docs(
    self,
    documents,
    generate_embeddings = False,
    embedding_function = None,
  ):
    if embedding_function and not callable(embedding_function):
      Utils.print_error_and_exit("Embedding Function must be a function or None")

    texts = [d.page_content for d in documents]
    metadatas = [d.metadata for d in documents]

    if embedding_function:
      return embedding_function(documents)

    embedding = self.__get_embeddings_from_docs(texts, self.__open_ai_api_key)


    """ print("All methods and attributes in faiss object")
    user_defined_methods_and_attributes = [name for name in dir(faiss) if not name.startswith('__')]
    print(user_defined_methods_and_attributes) """

    if generate_embeddings:
      # self.get_embeddings_from_docs(generate_embeddings, embedding_function)
      embeddings = embedding.embed_documents(texts)
      index = faiss.IndexFlatIP(len(embeddings[0]))
      vector = np.array(embeddings, dtype=np.float32)
      index.add(vector)
    else:
      try:
        embeddings_file_path = self.__get_embeddings_path(self.__database_id, self.__database_name)
        print("embeddings_file_path: ", embeddings_file_path)
        vector = np.load(embeddings_file_path)
        index = faiss.IndexFlatIP(len(vector[0]))
        index.add(vector)
      except:
        Utils.print_error_and_exit(f"Database with name {self.__database_name} is not embedded. Please embed the database and try again.")

    documents = []

    for i, text in enumerate(texts):
      metadata = metadatas[i] if metadatas else {}
      documents.append(Document(page_content=text, metadata=metadata))
    index_to_docstore_id = {i: doc.metadata['objectId'] for i, doc in enumerate(documents)}
    print('index to doctore map')
    print(index_to_docstore_id)
    docstore = InMemoryDocstore(
        {index_to_docstore_id[i]: doc for i, doc in enumerate(documents)}
    )

    #ToDo: return Bdb VS from here
    faiss_vector_store = FAISS(embedding.embed_query, index, docstore, index_to_docstore_id)

    if generate_embeddings:
      file_path = self.__get_embeddings_path(self.__database_id, self.__database_name)
      doc_store_id_to_index = {index_to_docstore_id[i]: i for i in range(len(index_to_docstore_id))}
      print(doc_store_id_to_index)
      self.__persist_embeddings(file_path, vector)
      self.__store_embedding_data(file_path, doc_store_id_to_index)
    return faiss_vector_store;

  def __get_embeddings_path(self, database_id, database_name):
    embeddings_file_path_prefix = os.environ.get("EMBEDDINGS_FILE_PATH_PREFIX", None)
    print("embeddings_file_path_prefix: ", embeddings_file_path_prefix)
    return f"{embeddings_file_path_prefix if embeddings_file_path_prefix else ''}{str(database_id)}_{database_name}_embeddings.npy"


  def __persist_embeddings(self, file_path, embeddings):
    # Convert embeddings to a NumPy array and persist to file system
    embeddings_array = np.array(embeddings)
    np.save(file_path, embeddings_array)

  def __store_embedding_data(
    self, file_path, mappings
  ):
    data = {
      'databaseId': self.__database_id,
      "path": file_path,
      "mappings": mappings,
    }
    doc = {"id": str(self.__database_id) + "_" + self.__database_name, "data": data}

    self.__upsert_file_path_data_into_vector_bucket(doc)

  """ def __create_embeddings(self, documents):
    embeddings = OpenAIEmbeddings(openai_api_key=self.__open_ai_api_key)
    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store """

  def ask_and_get_answers(self, q, k=3):
    if not self.is_embedded():
      Utils.print_error_and_exit(f"The database with name {self.__database_name} is not embedded. Please embed the database and try again.")

    llm = ChatOpenAI(
      model="gpt-3.5-turbo", temperature=1, openai_api_key=self.__open_ai_api_key
    )
    v_store = self.__get_vector_store()
    retriever = v_store.as_retriever(search_kwargs={"k": k})
    chain = RetrievalQA.from_chain_type(
      llm=llm, chain_type="stuff", retriever=retriever
    )
    answer = chain.run(q)
    print("answer: ", answer)
    return answer

  def __calculate_embedding_cost(self, texts):
    enc = tiktoken.encoding_for_model("text-embedding-ada-002")
    total_tokens = sum([len(enc.encode(page.page_content)) for page in texts])
    return total_tokens, total_tokens / 1000 * 0.0004
    # return len(texts), 0

  def __get_all_records_for_database(self):
    db = Database(self.__berry_db_api_key, self.__bucket_name, self.__database_id, self.__database_name)
    records = db.get_all_documents()
    print(f"A total of {len(records)} fetched")
    print(records)
    return records

  """ def __get_all_dbs_for_api_key(self):
    databases = Database(self.__berry_db_api_key, self.__bucket_name, self.__database_id, self.__database_name)
    if databases is None or len(databases) == 0:
      Utils.print_error_and_exit(
          f"No databases found for the api key {self.__berry_db_api_key}"
      )
    else:
      print("All Database names are: ", str(databases.keys()))
      return databases.keys() """

  """ def __get_selected_database_index(self, database_list, database_name, bdb_api_key):
    index = 0
    if database_list is None:
      # raise HTTPException(status_code=400, detail=f'No databases found for the api key {bdb_api_key}')
      Utils.print_error_and_exit(
          f"No databases found for the api key {bdb_api_key}"
      )
    if database_name is not None:
      database_list = list(database_list)
      try:
        index = database_list.index(database_name)
      except:
        # raise HTTPException(status_code=400, detail=f'No database with name {database_name} found for the api key {bdb_api_key}')
        Utils.print_error_and_exit(
            f"No database with name {database_name} found for the api key {bdb_api_key}"
        )
    return index """

  def __load_JSON(self, records):
    # loader = BerryDBJSONCSVLoader(json_data=records, text_content=False)
    loader = BerryDBJSONLoader(
        json_data=records, jq_schema=".[]", text_content=False
    )
    return loader.load()

  def __upsert_file_path_data_into_vector_bucket(self, data):
    berryDb_vectors_bkt = Database(self.__berry_db_api_key, "Vectors", self.__database_id, self.__database_name,)
    berryDb_vectors_bkt.upsert_document(data)

  def is_embedded(self):
    berryDb_vectors = Database(self.__berry_db_api_key, "Vectors", self.__database_id, self.__database_name)
    # query = f'Select * from Vectors where databaseId = {db_id}'
    query = f"SELECT COUNT(*) AS count FROM `Vectors` WHERE databaseId = '{self.__database_id}'"
    result = berryDb_vectors.query(query)
    print("result: ", result)
    try:
        count = result[0]["count"]
    except:
        count = 0
    return bool(count)

generic_error_message = "Oops! something went wrong. Please try again later."


class Utils:
  @classmethod
  def get_headers(self, api_key: str, content_type: str = "application/json"):
    return {"Content-Type": content_type, "x-api-key": api_key, "Accept": "*/*"}

  @classmethod
  def handleApiCallFailure(self, res, status_code):
    if status_code == 401:
      self.__print_error_and_exit(
        "You are Unauthorized. Please check your API Key"
      )
    if res.get("errorMessage", None):
      errMsg = res["errorMessage"]
    else:
      errMsg = generic_error_message if (res == None or res == "") else res
    raise Exception(errMsg)

  @classmethod
  def print_error_and_exit(self, msg=None):
    msg = msg if msg is not None else generic_error_message
    print(msg)
    raise Exception(msg)
    # exit()

class BerryDBJSONLoader(BaseLoader):
    """Loads a JSON file using a jq schema.

    Example:
        [{"text": ...}, {"text": ...}, {"text": ...}] -> schema = .[].text
        {"key": [{"text": ...}, {"text": ...}, {"text": ...}]} -> schema = .key[].text
        ["", "", ""] -> schema = .[]
    """

    def __init__(
        self,
        json_data: Union[List, Dict],
        jq_schema: str,
        content_key: Optional[str] = None,
        metadata_func: Optional[Callable[[Dict, Dict], Dict]] = None,
        text_content: bool = True
    ):
        """Initialize the JSONLoader.

        Args:
            json_data (Union[List, Dict]): JSON data to be parsed.
            jq_schema (str): The jq schema to use to extract the data or text from
                the JSON.
            content_key (str): The key to use to extract the content from the JSON if
                the jq_schema results to a list of objects (dict).
            metadata_func (Callable[Dict, Dict]): A function that takes in the JSON
                object extracted by the jq_schema and the default metadata and returns
                a dict of the updated metadata.
            text_content (bool): Boolean flag to indicate whether the content is in
                string format, default to True.
        """
        try:
            import jq  # noqa:F401
        except ImportError:
            raise ImportError(
                "jq package not found, please install it with `pip install jq`"
            )
        self._json_data = json_data
        self._jq_schema = jq.compile(jq_schema)
        self._content_key = content_key
        self._metadata_func = metadata_func
        self._text_content = text_content

    def load(self) -> List[Document]:
        """Load and return documents from the JSON file."""
        #pdb.set_trace()
        docs: List[Document] = []
        self._parse(self._json_data, docs)
        return docs

    def _parse(self, content: str, docs: List[Document]) -> None:
        """Convert given content to documents."""
        data = self._jq_schema.input(content)
        # Perform some validation
        # This is not a perfect validation, but it should catch most cases
        # and prevent the user from getting a cryptic error later on.
        if self._content_key is not None:
            self._validate_content_key(data)

        for i, sample in enumerate(data, len(docs) + 1):
            metadata = dict(
                source='json input',
                row=i,
                objectId = sample.get('objectId')
            )
            text = self._get_text(sample=sample, metadata=metadata)
            docs.append(Document(page_content=text, metadata=metadata))

    def _get_text(self, sample: Any, metadata: dict) -> str:
        """Convert sample to string format"""
        if self._content_key is not None:
            content = sample.get(self._content_key)
            if self._metadata_func is not None:
                # We pass in the metadata dict to the metadata_func
                # so that the user can customize the default metadata
                # based on the content of the JSON object.
                metadata = self._metadata_func(sample, metadata)
        else:
            content = sample

        if self._text_content and not isinstance(content, str):
            raise ValueError(
                f"Expected page_content is string, got {type(content)} instead. \
                    Set `text_content=False` if the desired input for \
                    `page_content` is not a string"
            )

        # In case the text is None, set it to an empty string
        elif isinstance(content, str):
            return content
        elif isinstance(content, dict):
            return json.dumps(content) if content else ""
        else:
            return str(content) if content is not None else ""

    def _validate_content_key(self, data: Any) -> None:
      """Check if a content key is valid"""
      sample = data.first()
      if not isinstance(sample, dict):
        raise ValueError(
          f"Expected the jq schema to result in a list of objects (dict), \
              so sample must be a dict but got `{type(sample)}`"
        )

      if sample.get(self._content_key) is None:
        raise ValueError(
          f"Expected the jq schema to result in a list of objects (dict) \
            with the key `{self._content_key}`"
        )

      if self._metadata_func is not None:
        sample_metadata = self._metadata_func(sample, {})
        if not isinstance(sample_metadata, dict):
          raise ValueError(
            f"Expected the metadata_func to return a dict but got \
              `{type(sample_metadata)}`"
          )

if __name__ == "__main__":
   pass