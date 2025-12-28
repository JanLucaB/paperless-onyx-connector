## Introduction

**paperless-onyx-connector** is a small bridge between **Paperless-ngx** and **Onyx**.

It polls Paperless-ngx every *X seconds* and looks for documents that have a dedicated **queue tag**. For each queued document, it fetches the document metadata and **ingests it into Onyx**.  
**Important:** The actual PDF/image file is *not* required — the connector only uses the document **title** and the extracted **content** from Paperless’ `content` field.

To keep sources traceable, the connector also adds a **link back to the original document in Paperless-ngx** to the Onyx file object, so you can jump directly to the source later.

### Onyx setup

On the Onyx side you need to create a **File Connector**. Due to a current Onyx limitation, creating a connector requires uploading a file — you can simply upload an **empty `.txt`** file.  
After creation, you can retrieve the required **File Connector ID** from the browser URL.

> Note: Because of technical limitations on the Onyx side, it is currently **not possible to delete already ingested files**.

### Paperless-ngx setup

In Paperless-ngx you should create **two tags**:
1. A **queue tag** that marks documents which should be transferred to Onyx.
2. A **done tag** that is applied after a successful ingest, so you can continue processing the document using Paperless workflows.

### Tip: Better OCR results

If you want significantly better OCR output than Paperless’ built-in OCR, have a look at **paperless-gpt** (https://github.com/icereed/paperless-gpt). It can greatly improve the extracted `content` quality, which directly improves what gets ingested into Onyx.


## docker-compose.yml exmple:
```yml
services:
  paperless-onyx-connector:
    image: jlbudde/paperless-onyx-connector:latest
    restart: unless-stopped
    environment:
      PAPERLESS_BASE_URL: "https://paperless.example.com" # Base URL of your Paperless-ngx instance
      PAPERLESS_API_KEY: "XXX" # API key used to authenticate against Paperless-ngx
      PAPERLESS_QUEUED_TAG_ID: "1" # Tag ID for documents that should be queued for syncing
      PAPERLESS_DONE_TAG_ID: "2" # Tag ID for documents that were successfully synced/processed
      ONYX_BASE_URL: "https://onyx.example.com" # Base URL of your Onyx instance
      ONYX_API_KEY: "XXX" # API key used to authenticate against Onyx
      ONYX_CONNECTOR_ID: "2" # Connector ID in Onyx to use for this integration
      SYNC_DELAY_SECONDS: "5" # Delay (in seconds) between sync cycles
      TZ: "Europe/Berlin" # servers time zone
```