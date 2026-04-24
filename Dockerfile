FROM python:3.13-slim

WORKDIR /app

COPY . .

ENV HOST=0.0.0.0
ENV PORT=4280
ENV DB_PATH=/app/data/portfolio_studio.db

EXPOSE 4280

CMD ["python", "server.py"]
