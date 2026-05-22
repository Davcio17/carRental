FROM python:3.14-slim AS builder

WORKDIR /build
COPY requirements.txt .

ENV PIP_NO_CACHE_DIR=1

RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt


FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN useradd -m -u 1000 myuser

WORKDIR /home/myuser/app

COPY --from=builder /install /usr/local
COPY --chown=myuser:myuser . .

USER myuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]