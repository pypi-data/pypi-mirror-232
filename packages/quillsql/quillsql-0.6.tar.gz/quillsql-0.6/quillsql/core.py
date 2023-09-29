import psycopg2
import requests

class Quill:
    def __init__(
        self,
        private_key,
        database_connection_string,
    ):
        self.private_key = private_key
        self.database_connection_string = database_connection_string
        self.main_pool = psycopg2.connect(database_connection_string)

    def query(self, org_id, data):
        metadata = data["metadata"]

        
        target_pool = self.main_pool
        task = metadata["task"]
        print("task", task)
       

        headers = {"Authorization": f"Bearer {self.private_key}"}

        if task == "query":
            try:
                query = metadata["query"]

                url = "https://quill-344421.uc.r.appspot.com/validate"
                headers = {
                    "Authorization": f"Bearer {self.private_key}"
                }

                data = {
                    "query": query,
                    "orgId": org_id,
                    "filters": []
                }

                response = requests.post(url, json=data, headers=headers)
                response_data = response.json()

                field_to_remove = response_data.get("fieldToRemove")

                print('response_data', response_data)
                cursor = target_pool.cursor()
                cursor.execute(response_data["query"])
                query_result = cursor.fetchall()
                print('testing', query_result)
                names = [desc[0] for desc in cursor.description]
                fields = [{"name": desc[0], "dataTypeID": desc[1]} for desc in cursor.description if desc[0] != field_to_remove]
                rearrange_fields = any(field["dataTypeID"] == 1082 or field["name"] == "created_at" for field in fields)
                if rearrange_fields:
                    # Sort fields so that the entry with dataTypeID = 1082 or name "created_at" is the first element
                    fields.sort(key=lambda x: (x["dataTypeID"] != 1082, x["name"] != "created_at"))
                fields.sort(key=lambda x: x["dataTypeID"] != 1082)
                formatted_result = {
                    "fields": fields,
                    "rows": [dict(zip(names, row)) for row in query_result],
                }

                # Remove the undesired field from the row dictionaries
                for row in formatted_result["rows"]:
                    if field_to_remove in row:
                        del row[field_to_remove]
                    row['created_at'] = row['created_at'].strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

                

                print('formatted result', formatted_result)

                return formatted_result

            except Exception as err:
                return {"error": str(err), "errorMessage": str(err) if err else ""}

        elif task == "config":
            try:
                print('here we are in config')
                response = requests.get(
                    "https://quill-344421.uc.r.appspot.com/config",
                    params={
                        "orgId": org_id,
                        "name": metadata.get("name")
                    },
                    headers={
                        "Authorization": f"Bearer {self.private_key}",
                    },
                )
                dash_config = response.json()

                print('common sense')

               
                if dash_config and dash_config["filters"]:
                    for i, filter in enumerate(dash_config["filters"]):
                        # run query
                        print('stuff', dash_config)
                        cursor = target_pool.cursor()
                        cursor.execute(filter["query"])
                        rows = cursor.fetchall()

                        # Update the options for each filter with the rows
                        dash_config["filters"][i]["options"] = rows

                if not dash_config:
                    dash_config["filters"] = []
                    
                return dash_config
            
            except Exception as err:
                return {"error": str(err), "errorMessage": str(err) if err else ""}

        elif task == "create":
            try:
                print('check create', metadata, org_id)
                response = requests.post(
                    "https://quill-344421.uc.r.appspot.com/item",
                    json=metadata,
                    params={"orgId": org_id},
                    headers=headers,
                ).json()

                return response
            except Exception as err:
                return {"error": str(err), "errorMessage": str(err) if err else ""}

        elif task == "item":
            try:
                resp = requests.get(
                    "https://quill-344421.uc.r.appspot.com/selfhostitem",
                    params={"id": metadata.get("id"), "orgId": org_id},
                    headers={"Authorization": f"Bearer {self.private_key}"},
                )
                resp_data = resp.json()
                data_to_send = {
                "query": resp_data["queryString"],
                "orgId": org_id,
                "filters": metadata.get("filters")
                }

                response = requests.post(
                    "https://quill-344421.uc.r.appspot.com/validate",
                    json=data_to_send,
                    headers={"Authorization": f"Bearer {self.private_key}"}
                )
                response_data = response.json()
                

                field_to_remove = response_data["fieldToRemove"] if response_data["fieldToRemove"] else None

                with target_pool.cursor() as cursor:
                    cursor.execute(response_data["query"])
                    query_result = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    rows = [dict(zip(columns, row)) for row in query_result]
                    fields = [column for column in columns if column != field_to_remove]
                    rows = [
                        {
                            key: value
                            for key, value in row.items()
                            if key != field_to_remove
                        }
                        for row in rows
                    ]

                return {**resp_data, "fields": fields, "rows": rows}

            except Exception as err:
                return {"error": str(err), "errorMessage": str(err) if err else ""}