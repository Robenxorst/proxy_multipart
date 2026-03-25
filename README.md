# Multi-Service Integration & NLP Processing API

Production-ready FastAPI service that combines multiple independent business use-cases into a single deployable microservice due to infrastructure constraints.

## 📌 Overview
This service aggregates three independent business solutions:
1) Integration proxy for external API (4me);
2) JSON field translation (RU → EN) for external system (BTI);
3) NLP-based address matching (MosAvtoDor project)

Although these components are logically independent, they are deployed as a single service due to time and infrastructure constraints.

## 🧩 Services

**1. MosAvtoDor NLP Matching (`POST /mos_avto_dor`)**

*📍 Problem*

User provides address in free-form speech, which must be matched against a structured database.

*⚙️ Solution*

Implemented a rule-based NLP pipeline for address matching.

*🧠 NLP Pipeline*
- Text normalization (cleaning noise)
- Lemmatization
- Canonical transformation
- Approximate string matching (RapidFuzz / Levenshtein)
- Scoring + threshold decision

*📤 Output:*

`result` — match / no match;
`address` — best match;
`score` — similarity %;

*Example:*
```
curl -X POST -H "Content-Type: application/json" -d '{"address":"Я нахожусь на улице Бубнова, дом 13"}' http://0.0.0.0:8091/mos_avto_dor
```
*Answer:*
```
{"result":"False","address":"М-4 «Дон»- Михнево","score":"60.61"}
```

**2. 4me Integration Proxy (`POST /proxy`)**

*📍 Problem*

Voice assistants operate with JSON only, while the external API (4me) requires multipart/form-data.

*⚙️ Solution*

Implemented a proxy service that:
1) Accepts `JSON` requests from the voice assistant.
2) Converts them into `multipart/form-data`.
3) Sends requests to `4me API`.
4) Parses and normalizes response.

*Key logic*
- Async API communication via `httpx`;
- Data transformation (JSON ↔ form-data);
- Company field extraction and cleanup;
- Error handling and logging;

**3. BTI JSON Translator (`GET /mos_gor_bti`)**

*📍 Problem*

External API returns JSON with **Cyrillic field names**, which are not compatible with downstream systems.

*⚙️ Solution*
Implemented a recursive JSON transformer that:
1) Fetches data by phone number.
2) Translates field names from Russian to English.
3) Preserves nested JSON structure.

*Key logic*
- Recursive traversal of JSON (dict / list);
- Key mapping (RU → EN);
- Async API integration;

## Tech Stack

- Python 3.x;
- FastAPI;
- httpx (async HTTP client);
- RapidFuzz (string similarity);
- Docker / Docker Compose;

## 🔮 Future Improvements

*NLP pipeline:* Replace Levenshtein with `embeddings + cosine similarity` and `semantic search`.

*Architecture:* 
- Split into independent services;
- Add API gateway layer;

*General:*
- Add monitoring & metrics;
- Improve error observability;

## ▶️ Run Locally

```
git clone git@github.com:Robenxorst/proxy_multipart.git
cd proxy_multipart
```

Before running the service, create a `.env` file:
```
touch .env
```

Fill in the required environment variables:
```
AUTH_TOKEN=your_token_here
TARGET_URL=https://api.example.com
URL_BTI=https://bti.example.com
AUTH_BTI=your_basic_auth_here
THRESHOLD=80
```

⚠️ Dont commit `.env` to the repository.

Build and run service:
```
docker-compose up --build
```
