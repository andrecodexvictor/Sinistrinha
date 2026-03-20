FROM python:3.12-slim

WORKDIR /app

COPY probability_engine/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY probability_engine/ ./probability_engine/

EXPOSE 8001

CMD ["uvicorn", "probability_engine.main:app", "--host", "0.0.0.0", "--port", "8001"]
