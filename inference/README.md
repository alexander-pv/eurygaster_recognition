
Code to reproduce service preparation:
```bash
# Download weights and export models into bentoml
$ cd ./inference
$ python prepare_models.py  --tag v1.3.0 \
    --model_name \
    model_0d03affcc3fe4555217e01aee7d73fed7ebdf35a_binary_calib_dyn.onnx \
    model_4fa9730aef422d53cf1ccb3db93da78d68991301_multiclass_calib_dyn.onnx
    
# Check models in bentoml local storage
$ bentoml models list

$ bentoml build  # Build CPU version
$ bentoml build -f bentofile-gpu.yaml # Build GPU&CPU version
$ bentoml list # List prepared bentoml services
$ bentoml containerize erg:<BENTO_HASH> # Prepare docker container
```
Commit new Docker containers into DockerHub
```bash
$ docker tag <HASH> <DOCKERHUB_ADDRESS>:<BENTO_HASH>-cpu
$ docker tag <HASH> <DOCKERHUB_ADDRESS><BENTO_HASH>-cuda11.4
$ docker push <CONTAINER>
```