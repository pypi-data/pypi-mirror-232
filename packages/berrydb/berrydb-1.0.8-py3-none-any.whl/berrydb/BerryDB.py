import requests
import json
from utils.utils import Utils
from database.database import Database
from constants.constants import get_database_list_by_api_key_url, get_database_id_url, debug_mode


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

if __name__ == "__main__":
   pass