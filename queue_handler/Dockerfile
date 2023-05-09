FROM python:3.10-slim

WORKDIR /workspace
COPY . ./

RUN pip install .
WORKDIR /
RUN rm -rf /workspace
CMD python -m queue_handler
