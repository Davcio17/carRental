FROM python:3.11-slim

RUN useradd -m myuser
USER myuser

ENV PATH="/home/myuser/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

WORKDIR /home/myuser/app

COPY --chown=myuser:myuser requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

COPY --chown=myuser:myuser . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]