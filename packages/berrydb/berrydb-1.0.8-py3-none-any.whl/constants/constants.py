debug_mode = False

# BerryDB Base URLs
base_url = "https://app.berrydb.io"
berry_gpt_base_url = "http://gpt.berrydb.io:9090"

# Profile service endpoints
get_database_id_url = base_url + "/profile/database"
get_database_list_by_api_key_url = base_url + "/profile/database/list-by-api-key"

# Berrydb service endpoints
documents_url = base_url + "/berrydb/documents"
query_url = base_url + "/berrydb/query"
document_by_id_url = base_url + "/berrydb/documents/{}"
bulk_upsert_documents_url = base_url + "/berrydb/documents/bulk"

# ML backend endpoint
transcription_url = berry_gpt_base_url + "/transcription"
transcription_yt_url = berry_gpt_base_url + "/transcription-yt"
caption_url = berry_gpt_base_url + "/caption"

generic_error_message = "Oops! something went wrong. Please try again later."