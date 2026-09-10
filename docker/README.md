# Docker Setup for NVIDIA Isaac GR00T

Docker configuration for building and running a containerized GR00T environment with all dependencies pre-installed. A single `Dockerfile` supports both x86_64 and aarch64 (GB200, Grace Hopper) architectures. On aarch64, `torchcodec` is installed from the prebuilt wheel shipped under `scripts/deployment/dgpu/wheels/`; the build falls back to a source compile only if the wheel is missing.

## Prerequisites

- Docker (version 20.10+) and [perform post-installation setup](https://docs.docker.com/engine/install/linux-postinstall/) so you can run Docker commands without sudo. If you skip this setup, prefix the Docker commands below with `sudo`.
- NVIDIA Container Toolkit ([installation guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html))
- NVIDIA GPU with compatible drivers
- Bash shell
- Sufficient disk space (several GB)

## Building the Docker Image

From the repository root:

```bash
make -C docker build
```

This builds from `nvidia/cuda:12.8.0-devel-ubuntu24.04` and installs all dependencies into `/opt/gr00t-venv`. The image includes this fork at `/gr00t`, installed into `/opt/gr00t-venv`. Positronic launches that environment directly.

## Positronic base image

```bash
make -C docker build
make -C docker push IMAGE_TAG=my-branch
```

The Makefile publishes `positro/gr00t-base` with branch and commit tags. It does not replace
`latest`. Positronic's `GROOT_BASE_IMAGE` selects this image for its adapter build.

Fine-tuning defaults to the base checkpoint's saved model and modality configuration.
`--video-keys` selects the fine-tuning camera layout; omitted, it retains the checkpoint's views.
The policy server accepts `--model-path hf://nvidia/GR00T-N1.7-DROID` and downloads that snapshot.

## Running the Container

Run the included fork from `/gr00t`:

```bash
docker run -it --rm --gpus all \
    --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 \
    -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
    positro/gr00t-base:local
```

Inside the container:

```bash
cd /gr00t
uv run --no-sync python -c "import gr00t; print(gr00t.__file__)"
```

The image includes the fork and its locked environment at `/opt/gr00t-venv`.
The Hugging Face account must have access to the gated `nvidia/Cosmos-Reason2-2B` backbone.
Provide its token through the mounted Hugging Face cache or `HF_TOKEN`.

For development, mount a compatible fork checkout over `/gr00t`:

```bash
docker run -it --rm --gpus all --ipc=host \
    -v "$PWD:/gr00t" positro/gr00t-base:local
```

If its lockfile differs from the image, create a separate environment:

```bash
export UV_PROJECT_ENVIRONMENT=/gr00t/.venv
uv sync --locked --extra dev
source /gr00t/.venv/bin/activate
```

## Edge Device Containers

### Thor Container (Jetson Thor / CUDA 13)

The `gr00t-thor` image is built from `scripts/deployment/thor/Dockerfile` for Jetson Thor with CUDA 13 support:

```bash
bash docker/build.sh --profile=thor
```

For full Thor usage instructions (inference, benchmarks, bare metal setup), see the [Deployment & Inference Guide](../scripts/deployment/README.md#jetson-thor-setup).

### Spark Container (DGX Spark / CUDA 13)

The `gr00t-spark` image is built from `scripts/deployment/spark/Dockerfile` for DGX Spark with CUDA 13 support:

```bash
bash docker/build.sh --profile=spark
```

For full Spark usage instructions (inference, benchmarks, bare metal setup), see the [Deployment & Inference Guide](../scripts/deployment/README.md#dgx-spark-setup).

### Orin Container (Jetson Orin / CUDA 13.2)

The `gr00t-orin` image is built from `scripts/deployment/orin/Dockerfile` for Jetson Orin (JetPack 7.2, CUDA 13.2, Python 3.12):

```bash
bash docker/build.sh --profile=orin
```

For full Orin usage instructions (inference, benchmarks, bare metal setup), see the [Deployment & Inference Guide](../scripts/deployment/README.md#jetson-orin-setup).

## Troubleshooting

**GPU not detected:**
- Verify NVIDIA Container Toolkit: `nvidia-container-toolkit --version`
- Restart Docker: `sudo systemctl restart docker`
- Test GPU access: `docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi`

**Permission errors:**
- Use `sudo` with Docker commands, or add your user to the `docker` group: `sudo usermod -aG docker $USER`

**Build failures:**
- Check disk space: `df -h`
- Clean Docker: `docker system prune -a`
- Rebuild: `bash docker/build.sh --no-cache`
