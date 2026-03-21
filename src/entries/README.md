# Entries Server

Stores and serves recent recognition scores and thumbnail icons for the Eurygaster app (login page carousel and recent entries table).

## Endpoints

- `GET /health` — Health check (returns 200 when DB is reachable).
- `POST /add_score/` — Add a recognition score and icon (JSON: `score`, `class_name`, `icon_b64`).
- `GET /get_score/?n=<int>` — Recent scores (default 10, max 500). Returns JSON array of `{DateTime, Score, Recognized}`.
- `GET /get_icons/?n=<int>` — Recent icon base64 strings (default 10, max 500).

## Configuration (environment)

| Variable | Default | Description |
|----------|---------|-------------|
| `ENTRIES_DATABASE` | `entries.db` | SQLite database path. For persistence, use a path in a mounted volume (e.g. `/data/entries.db`). |
| `SERVER_PORT` | `8084` | Server port. |
| `LIMIT_ENTRIES` | `50` | Max number of scores to keep; older ones are pruned. |
| `CLEAR_TIMING_MIN` | `5` | Interval (minutes) for pruning old entries. |
| `TIME_OFFSET_HRS` | `3` | Timezone offset for stored timestamps. |
| `ENTRIES_MAX_ICON_B64_LEN` | `3145728` | Max icon base64 length (bytes). Default 3 MiB. |

## Persistence

The default database path is `entries.db` in the working directory. To persist data across container restarts, set `ENTRIES_DATABASE` to a path in a mounted volume, e.g.:

```yaml
entries_server:
  environment:
    ENTRIES_DATABASE: /data/entries.db
  volumes:
    - entries-data:/data
```

## Build and run

```bash
pip install -r requirements.txt
python entries_server.py
```

Docker: build from this directory; the image runs `python entries_server.py` and listens on `SERVER_PORT`.
