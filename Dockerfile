FROM python:3.11-slim

WORKDIR /src
COPY app/requirements.txt /src/requirements.txt
RUN pip install --no-cache-dir -r /src/requirements.txt

# copy the app dir into /src/app so "import app" works
COPY app /src/app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
