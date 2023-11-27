FROM nvidia/cuda:12.0.0-devel-ubuntu20.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive
ENV HUGGINGFACE_HUB_ENABLE_HF_TRANSFER=1

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -y python3.10 python3-pip \
    git g++

RUN --mount=type=cache,target=/root/.cache/pip \
    CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install --upgrade --force-reinstall llama-cpp-python --no-cache-dir -q

COPY ./requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install --trusted-host pypi.python.org -r requirements.txt

COPY download_models.py .
RUN python3 download_models.py


RUN find /usr/local/ \( -type d -a -name test -o -name tests \) -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) -delete && \
    find . -type d -name "tests" -exec rm -rv {} + && \
    find . -type d -name "__pycache__" -exec rm -rv {} + && \
    rm -rf ./{caffe2,wheel,pkg_resources,boto*,aws*,pip,pipenv,setuptools} && \
    rm -rf ./torch/test


#### Lean image ####
FROM nvidia/cuda:12.0.0-base-ubuntu20.04
COPY --from=builder /usr/local/lib/python3.10/dist-packages /usr/local/lib/python3.10/dist-packages
COPY --from=builder /usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu
COPY --from=builder /root/.cache/huggingface /root/.cache/huggingface

RUN apt-get update && \
    apt-get install -y python3.10  python3.10-distutils && \
    apt-get purge --auto-remove && \
    apt-get clean

ADD app /app
ADD data /data

COPY --from=builder ./llm.gguf /app/llm.gguf

WORKDIR /app

CMD python3.10 main.py