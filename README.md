### Eurygaster spp. classification service

Architecture:

![eurygaster_ml_service](./pics/eurygaster_ml_service.png)


Usage:

![login](./pics/web_login.png)

![recognition_example](./pics/recognition_example.gif)

#### How to prepare models cascade with BentoML
```bash
# Load models into BentoML
$ python prepare_models.py \
  --tag v1.3.0 \
  --model_name \
    model_0d03affcc3fe4555217e01aee7d73fed7ebdf35a_binary_calib_dyn.onnx \
    model_4fa9730aef422d53cf1ccb3db93da78d68991301_multiclass_calib_dyn.onnx

# Prepare inference service
$ bentoml build  # Standard BentoML service
$ bentoml build -f bentofile-gpu.yaml # BentoML service with GPU support
$ bentoml containerize eurygaster:<BENTO_TAG>

# Test models with BentoML
$ make bento_test
```

#### How to deploy the system


```bash
## CPU-supported minimal version
$ make up_cpu_system_minimal
## CPU-supported version with error tracking
$ make up_cpu_system
## GPU-supported minimal version
$ make up_gpu_system_minimal
## GPU-supported version with error tracking
$ make up_gpu_system
```

#### How to run load tests
```bash
$ make load_test
```

#### How to connect GlitchTip to Grafana
* Add [plugin](https://grafana.com/grafana/plugins/grafana-sentry-datasource/?tab=installation) to `./grafana/plugins/grafana-sentry-datasource`
* Add auth token according to [integration description](https://glitchtip.com/documentation/integrations)
