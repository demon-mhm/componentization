FROM python:3.12-slim-bookworm
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY --from=base /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages 
COPY wire/adapter/*.py .
ENTRYPOINT ["uvicorn"]
ARGUMENTS ["main:app"]
