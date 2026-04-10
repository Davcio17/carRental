FROM python:3.11-slim
RUN useradd -m myuser
USER myuser
WORKDIR /home/myuser/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]