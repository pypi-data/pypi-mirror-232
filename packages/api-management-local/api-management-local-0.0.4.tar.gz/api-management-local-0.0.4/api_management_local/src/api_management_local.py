# TODO: This is an example file which you should delete after implementing
from dotenv import load_dotenv
import json
from circles_local_database_python.connector import Connector
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from circles_local_database_python.connector import Connector
from circles_local_database_python.generic_crud import GenericCRUD
load_dotenv()

# Setup the logger: change YOUR_REPOSITORY variable name and value
YOUR_REPOSITORY_COMPONENT_ID = 212  # ask your team leader for this integer
YOUR_REPOSITORY_COMPONENT_NAME = "api-management-local-python-package"
DEVELOPER_EMAIL = "heba.a@circ.zone"
object1 = {
    'component_id': YOUR_REPOSITORY_COMPONENT_ID,
    'component_name': YOUR_REPOSITORY_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': DEVELOPER_EMAIL
}
logger=Logger.create_logger(object=object1)
class ExampleClass(GenericCRUD):
    def __init__(self) -> None:
        pass

    @staticmethod
    def insert_data_into_table(table_name, data):
        try:
            json_data = {
                'api_type_id': data[0], 
                'endpoint': data[1], 
                'outgoing_header': data[2], 
                'outgoing_body': data[3], 
                 'outgoing_body_signigicant_fields_hash': data[4], 
                'incoming_message': data[5]  }
            crud_instance = GenericCRUD(schema_name='api_call')
            crud_instance.insert(table_name=table_name, json_data=json_data)
        except Exception as e:
            raise(f"Error inserting data: {str(e)}")
            
    @staticmethod
    def get_limits_by_api_type_id(table_name, api_type_id)->list:
        try:
           api_type_id_str="api_type_id="+api_type_id
           crud_instance = GenericCRUD(schema_name='api_limit')
           list=crud_instance._select_by_where(table_name=table_name,select_clause_value=api_type_id_str)
           return list 
        except Exception as e:
            raise(f"Error getting data: {str(e)}")  
            
    @staticmethod
    def get_actual_by_type_id(table_name, api_type_id, time) -> int:
        connection = Connector.connect("api_call")
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT NOW()")
            current_datetime = cursor.fetchone()[0]
            query = f"SELECT COUNT(*) FROM {table_name} WHERE api_type_id={api_type_id} AND TIMESTAMPDIFF(HOUR, created_timestamp, '{current_datetime}') <= {time}"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            raise(f"Error: {str(e)}")
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def  get_json_with_only_sagnificant_fields_by_api_type_id(table_name, json1, api_type_id)-> json:
        connection = Connector.connect("api_type")
        try:
            cursor = connection.cursor()
            query = f"SELECT field_name FROM {table_name} WHERE api_type_id = %s"
            cursor.execute(query, (api_type_id,))
            significant_fields = [row[0] for row in cursor.fetchall()]
            data = json.loads(json1)
            filtered_data = {key: data[key] for key in significant_fields if key in data}
            filtered_json = json.dumps(filtered_data)
            return filtered_json

        except Exception as e:
            raise(f"Error: {e}")
        finally:
            connection.close()

