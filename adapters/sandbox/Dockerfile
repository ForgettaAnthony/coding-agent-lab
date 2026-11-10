FROM python:3.11-slim

RUN python -m pip install --no-cache-dir pytest==8.3.5 \
    && groupadd --gid 10001 runner \
    && useradd --create-home --uid 10001 --gid 10001 runner

ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /workspace
USER 10001:10001

CMD ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider"]
