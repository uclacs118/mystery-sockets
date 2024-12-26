FROM python:3.12-slim-bookworm

WORKDIR /app
RUN pip install flask
COPY telephone/app.py .
CMD ["python", "app.py"]