from local_cahce import cache_until_midnight
from db_manager import DatabaseManager

connection_pool = {}
connection_pool[key] = DatabaseManager({
    
})

@cache_until_midnight
def get_db_mapping(dataset_id, as_of_date):
    db_mapping = call_api_logic()

    return db_mapping

def call_catalogue_service():
    return {}

def get_db_connection(dataset_id, as_of_date):
    db_mapping = get_db_mapping(dataset_id, as_of_date)

