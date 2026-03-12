# Inference bentos (Python 3.10, BentoML 1.0.16).
# Use project-local BentoML store so models are not mixed with other Python envs.
# Run from inference/ with: uv sync && make prepare && make build-all

export BENTOML_HOME := $(CURDIR)/bentoml

.PHONY: build-cpu build-gpu build-all list prepare models-list containerize clean-store

prepare:
	uv run python prepare_models.py --tag v1.3.0 \
		--model_name \
		model_0d03affcc3fe4555217e01aee7d73fed7ebdf35a_binary_calib_dyn.onnx \
		model_4fa9730aef422d53cf1ccb3db93da78d68991301_multiclass_calib_dyn.onnx

models-list:
	uv run bentoml models list

build-cpu:
	uv run bentoml build -f bentofile.yaml

build-gpu:
	uv run bentoml build -f bentofile-gpu.yaml

build-all: build-cpu build-gpu

list:
	uv run bentoml list

# Remove entire BentoML store (all bentos and models). Run from inference/ with: make clean-store
clean-store:
	rm -rf $(BENTOML_HOME)
	@echo "Deleted all bentos and models from $(BENTOML_HOME)"

# Build Docker image from a bento (use BENTO_TAG=eurygaster:<hash>, or run 'make list' to see tags)
# BentoML 1.0.16's containerize has a bug with some option types; we use a wrapper that patches it.
containerize:
	@test -n "$(BENTO_TAG)" || (echo "Usage: make containerize BENTO_TAG=eurygaster:<hash>"; exit 1)
	uv run python scripts/containerize.py $(BENTO_TAG)
