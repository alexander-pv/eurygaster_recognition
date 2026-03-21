#### Code to reproduce service preparation

```bash
$ export BENTOML_HOME=$(pwd)/bentoml # Important for correct bentoml behavior
$ uv sync
$ make clean-store          # Cleans BentoML storage
$ make prepare              # Downloads ONNX and saves models into bentoml/ under BENTOML_HOME (Python 3.10)
$ make models-list          # List models in project store
$ make build-cpu            # or make build-gpu / make build-all
$ make list
```


Build Docker images from bentos:

`bentoml containerize` fails on BentoML 1.0.16 (NotImplementedError for some Docker build option types). Use the project wrapper instead:

```bash
# From src/inference/ (so BENTOML_HOME is used)
$ make containerize BENTO_TAG=eurygaster:<BENTO_HASH>
# or
$ uv run python scripts/containerize.py eurygaster:<BENTO_HASH>
```

Get `<BENTO_HASH>` from `make list` (e.g. `eurygaster:hwve3ba5q24qx57t`).

Commit new Docker containers into DockerHub:

```bash
$ docker tag <CPU_IMAGE_ID> <DOCKERHUB_ADDRESS>:<BENTO_HASH>-cpu
$ docker tag <GPU_IMAGE_ID> <DOCKERHUB_ADDRESS>:<BENTO_HASH>-cuda11.4
$ docker push <CONTAINER>
```
