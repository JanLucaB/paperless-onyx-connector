import requests
import time

from utils import get_environment_str, get_environment_int, log


PAPERLESS_BASE_URL: str = get_environment_str('PAPERLESS_BASE_URL')
PAPERLESS_API_KEY: str = get_environment_str('PAPERLESS_API_KEY')
PAPERLESS_QUEUED_TAG_ID: int = get_environment_int('PAPERLESS_QUEUED_TAG_ID')
PAPERLESS_DONE_TAG_ID: int = get_environment_int('PAPERLESS_DONE_TAG_ID')

ONYX_BASE_URL: str = get_environment_str('ONYX_BASE_URL')
ONYX_API_KEY: str = get_environment_str('ONYX_API_KEY')
ONYX_CONNECTOR_ID: int = get_environment_int('ONYX_CONNECTOR_ID')

SYNC_DELAY_SECONDS: int = get_environment_int('SYNC_DELAY_SECONDS')


PAPERLESS_HEADER = {'Authorization': f'Token {PAPERLESS_API_KEY}', 'Content-Type': 'application/json'}
ONYX_HEADER = {'Authorization': f'Bearer {ONYX_API_KEY}', 'Content-Type': 'application/json'}


def sync_paperless_to_onyx():
    while True:
        queued_documents_response = requests.get(f'{PAPERLESS_BASE_URL}/api/documents/?tags__id__all={PAPERLESS_QUEUED_TAG_ID}', headers=PAPERLESS_HEADER)
        queued_documents = queued_documents_response.json().get('results', [])

        if len(queued_documents) == 0:
            break

        for queued_document in queued_documents:
            document_id = queued_document['id']
            document_title = queued_document['title']
            document_content = queued_document['content']

            log(f'Syncing document (ID: {document_id})...')

            document_data = {
                'document': {
                    'id': f'paperless-{document_id}',
                    'semantic_identifier': document_title,
                    'sections': [
                        {
                            'text': document_content,
                            'link': f'{PAPERLESS_BASE_URL}/documents/{document_id}/details'
                        }
                    ],
                    'source': 'file',
                    'metadata': {},
                },
                'cc_pair_id': ONYX_CONNECTOR_ID
            }

            ingestion_response = requests.post(
                f'{ONYX_BASE_URL}/api/onyx-api/ingestion',
                headers=ONYX_HEADER,
                json=document_data
            )

            if ingestion_response.status_code != 200:
                raise Exception(f'Failed to ingest document ID {document_id} into Onyx: {ingestion_response.text}')


            tags = queued_document['tags']

            tags.remove(PAPERLESS_QUEUED_TAG_ID)
            tags.append(PAPERLESS_DONE_TAG_ID)

            tag_response = requests.patch(
                f'{PAPERLESS_BASE_URL}/api/documents/{document_id}/',
                headers=PAPERLESS_HEADER,
                json={'tags': tags}
            )

            if tag_response.status_code != 200:
                raise Exception(f'Failed to update tags for document ID {document_id}: {tag_response.text}')
            
            log(f'Document (ID: {document_id}) synced successfully.')


if __name__ == '__main__':
    log('Started')

    while True:
        sync_paperless_to_onyx()
        time.sleep(SYNC_DELAY_SECONDS)