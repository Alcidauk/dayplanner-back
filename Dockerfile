FROM python:3.9

WORKDIR /app

COPY pyproject.tomk .
RUN pip install --no-cache-dir .

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"l

