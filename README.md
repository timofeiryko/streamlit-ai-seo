# AI SEO Content Suite

This Streamlit app orchestrates an SEO workflow for keyword research, topic ideation, long-form article drafting, and image prompt generation.

## Company configuration

- Company-specific context (meta brief, brand messaging, knowledge base, category tags) lives in `config/companies.yaml`.
- Each company entry defines:
  - `display_name` – shown in the sidebar selector.
  - `product_name` – used inside prompts when referring to the brand.
  - `meta_brief` – default brief pre-filled in the *Semantic Core* tab.
  - `article_instructions` – message inserted into article prompts (use `{product_name}` placeholder if you need the brand name).
  - `knowledge_base` – categories and supporting facts that are passed to every LLM prompt.
- The `default_company` key controls which configuration is preselected on startup.

To add a new company, duplicate an existing block, adjust the values, and ensure the YAML indentation is preserved. The app automatically provides a sidebar selector for any company listed in the file.

## Article writer modes

- Базовый режим использует структурированный промпт с бренд-инструкциями и текущей датой (для предотвращения устаревших фактов).
- Галочка `Enhanced creativity mode` в разделе статьи добавляет расширенный промпт: модель становится «расширенным ChatGPT», пишет быстрее, смелее и живее, но при этом сохраняет переданные ключевые слова.
- Все запросы выполняются через `gpt-5-mini` (без настройки температуры); дата автоматически подставляется в каждый промпт.

## Архитектура

- `services/llm.py` — единая точка работы с LLM: шаблоны промптов, генерация семантического ядра, кластеризация, статьи и промпты для изображений.
- `services/digest.py` — сбор новостей по RSS (окно 04:00–03:59 GMT+3), подготовка данных для дайджеста, логирование выпусков.
- `main.py` — только Streamlit-интерфейс: выбор компании, состояние сессии, вкладки и вызовы сервисного слоя.

## Daily digest

- Вкладка `🗞️ Daily Digest` собирает новости из RSS (`ForkLog`, `CoinDesk`, `Cointelegraph`, `The Block`, `Incrypted`, а также Nitter-фиды ключевых Twitter-аккаунтов).
- Временное окно жёстко задано: с 04:00 предыдущего дня до 03:59 текущего дня по GMT+3, чтобы исключить дубликаты между выпусками.
- Каждая генерация сохраняется в `logs/daily_digests.jsonl`; при попытке собрать дайджест с тем же набором ссылок, что и за последние два дня, пользователь увидит предупреждение.

## Установка с помощью `uv`

```bash
# создаём среду (uv создаст .venv в корне)
uv venv
source .venv/bin/activate

# устанавливаем зависимости из pyproject/uv.lock
uv install

# запуск приложения
streamlit run main.py
```
