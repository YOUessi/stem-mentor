FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
COPY backend /app/backend
COPY apps/web /app/apps/web
ENV PYTHONPATH=/app/backend STEM_MENTOR_DB=/app/backend/data/demo.sqlite3
EXPOSE 8000
CMD ["uvicorn","app.main:app","--app-dir","/app/backend","--host","0.0.0.0","--port","8000"]
