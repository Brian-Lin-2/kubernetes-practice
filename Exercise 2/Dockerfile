FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /src

COPY server.py .

ENV PORT=8000

EXPOSE 8000

CMD ["python", "server.py"]
