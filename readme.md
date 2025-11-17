# Terraform GPT
### Projektstruktur
```
terraformgpt/
├─ requirements.txt
├─ .env.example
├─ src/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ supabase_client.py
│  ├─ models.py
│  └─ ingest/
│     ├─ __init__.py
│     └─ example_ingest.py
```
Ingest example
```
python -m src.ingest.example_ingest
```


Example Script to retrieve data
```
python -m src.query.attributes --resource azurerm_storage_account --version 4.52.0
```

```
python -m src.llm.explain_resource --resource azurerm_storage_account --version 4.52.0 --language de
```