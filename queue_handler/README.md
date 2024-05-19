Message broker handler that sends new Eurygaster spp. images to an external storage.

#### Env variables

| ENV                       | Description                            |
|---------------------------|----------------------------------------|
| LOGURU_LEVEL              | loguru logging level                   |
| LOGURU_INIT               | Flag for loguru logger, 1/0            |
| RMQ_ADDR                  | RMQ address                            |
| RMQ_TOPIC                 | RMQ topic name                         |
| STORAGE_TYPE              | Type of storage to use for image       |
| MINIO_ADDR                | MinIO storage address                  |
| MINIO_ACCESS_KEY          | MinIO key                              |
| MINIO_SECRET_KEY          | MinIO secret                           |
| GLITCHTIP_DSN             | GlitchTip project DSN                  |
| GLITCHTIP_MAX_BREADCRUMBS | Total amount of breadcrumbs to capture |
| GLITCHTIP_DEBUG           | sentry_sdk debug flag                  |
| GLITCHTIP_SR              | The fraction of errors to send         |

#### How to install and run handler with default MinIO storage:

```bash
$ make install
$ STORAGE_TYPE=minio \
  MINIO_ADDR=http://<STORAGE_IP>:<STORAGE_PORT> \
  MINIO_ACCESS_KEY=<USER> \
  MINIO_SECRET_KEY=<PWD> \
  RMQ_ADDR=amqp://<USER>:<PWD>@<RMQ_IP>:<RMQ_PORT> \
  python -m queue_handler
```

#### How to add new storage type

1. Create a subclass of `StorageSaver` abstract class in `storage.py`.
2. Add new class into `StorageTypes` object in `storage.py`.
