#!/usr/bin/env python3
"""
Wrapper for `bentoml containerize` that:
- Patches BentoML's Docker builder to support argument types (int, float, dict).
- For GPU bentos: replaces the deadsnakes PPA Python install (which often fails
  with "Unable to locate package python3.10-dev") by a multi-stage copy from
  python:3.10-slim-bullseye (glibc-compatible with Ubuntu 20.04 CUDA base).

Run from inference/ with BENTOML_HOME set, e.g.:
  make containerize BENTO_TAG=eurygaster:<hash>
  uv run python scripts/containerize.py eurygaster:<TAG>
"""
from __future__ import annotations

import os
import sys
from itertools import chain

# Apply patch before bentoml.container is used
def _patch_bentoml_construct_args():
    from bentoml._internal.container import base

    Args = base.Arguments
    # Already registered: None, tuple, list, str, PathLike, bool

    @Args.construct_args.register(int)
    @Args.construct_args.register(float)
    def _numeric(self, args: int | float, opt: str = ""):
        if args is not None:
            self.extend((f"--{opt}", str(args)))

    @Args.construct_args.register(dict)
    def _dict_args(self, args: dict | None, opt: str = ""):
        if args is not None:
            self.extend(
                list(
                    chain.from_iterable(
                        (f"--{opt}", f"{k}={v}") for k, v in args.items()
                    )
                )
            )


_patch_bentoml_construct_args()


def _patch_gpu_dockerfile(dockerfile_path: str) -> None:
    """
    Patch BentoML-generated GPU Dockerfile: replace deadsnakes PPA Python install
    (which often fails: E: Unable to locate package python3.10-dev) with a
    multi-stage copy from python:3.10-slim-bullseye (glibc matches Ubuntu 20.04).
    """
    with open(dockerfile_path) as f:
        content = f.read()
    if "add-apt-repository ppa:deadsnakes/ppa" not in content or "python3.10-dev" not in content:
        return

    # 1) Add python-base stage before the cuda FROM (match BentoML-generated header)
    old_base = "# Block SETUP_BENTO_BASE_IMAGE\nFROM nvidia/cuda:"
    if old_base not in content:
        return
    # Use bullseye (Debian 11) so glibc matches Ubuntu 20.04; bookworm/slim has glibc 2.36+.
    content = content.replace(
        old_base,
        "# Block SETUP_BENTO_BASE_IMAGE\nFROM python:3.10-slim-bullseye AS python-base\n\nFROM nvidia/cuda:",
        1,
    )

    # 2) Replace deadsnakes block. BentoML generates RUN with BuildKit mount options.
    deadsnakes_block = (
        "RUN --mount=type=cache,target=/var/lib/apt --mount=type=cache,target=/var/cache/apt \\\n"
        "    set -eux && \\\n"
        "    apt-get install -y --no-install-recommends --allow-remove-essential software-properties-common && \\\n"
        "    # add deadsnakes ppa to install python\n"
        "    add-apt-repository ppa:deadsnakes/ppa && \\\n"
        "    apt-get update -y && \\\n"
        "    apt-get install -y --no-install-recommends --allow-remove-essential curl python3.10 python3.10-dev python3.10-distutils\n\n"
        "RUN ln -sf /usr/bin/python3.10 /usr/bin/python3 && \\\n"
        "    ln -sf /usr/bin/pip3.10 /usr/bin/pip3\n\n"
        "RUN curl -O https://bootstrap.pypa.io/get-pip.py && \\\n"
        "    python3 get-pip.py && \\\n"
        "    rm -rf get-pip.py"
    )
    replacement = (
        "COPY --from=python-base /usr/local /usr/local\n"
        'ENV PATH="/usr/local/bin:$PATH"\n'
        "RUN ln -sf /usr/local/bin/python3.10 /usr/bin/python3.10 && ln -sf /usr/local/bin/python3 /usr/bin/python3 && ln -sf /usr/local/bin/pip3 /usr/bin/pip3"
    )
    if deadsnakes_block not in content:
        return
    content = content.replace(deadsnakes_block, replacement, 1)

    with open(dockerfile_path, "w") as f:
        f.write(content)


# Now run the real containerize (same as CLI)
def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/containerize.py BENTO_TAG [e.g. eurygaster:hwve3ba5q24qx57t]", file=sys.stderr)
        sys.exit(1)
    bento_tag = sys.argv[1]

    import bentoml
    from bentoml import container
    from simple_di import inject, Provide
    from bentoml._internal.container import construct_containerfile
    from bentoml._internal.container import get_backend
    from bentoml._internal.container import enable_buildkit
    from bentoml._internal.container import determine_container_tag
    from bentoml._internal.configuration.containers import BentoMLContainer

    if not container.health("docker"):
        print("Docker backend is not healthy. Install Docker and ensure it is running.", file=sys.stderr)
        sys.exit(1)

    # Resolve image tag (e.g. eurygaster:idieomq5rckqxtm6) so the image appears in docker images
    image_tag = determine_container_tag(bento_tag)

    # Build with Dockerfile patch for GPU bentos (deadsnakes install fix)
    @inject
    def build_with_gpu_patch(
        _bento_store=Provide[BentoMLContainer.bento_store],
    ):
        bento = _bento_store.get(bento_tag)
        builder = get_backend("docker")
        with construct_containerfile(
            bento,
            features=None,
            enable_buildkit=enable_buildkit(builder=builder),
        ) as (context_path, dockerfile_path):
            _patch_gpu_dockerfile(dockerfile_path)
            return builder.build(
                file=dockerfile_path,
                context_path=context_path,
                tag=image_tag,
            )

    result = build_with_gpu_patch()
    if result is None:
        sys.exit(1)
    print(f"Successfully built image for {bento_tag}")


if __name__ == "__main__":
    main()
