FROM ollama/ollama:latest

USER root
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY ./ollama-entrypoint.sh /ollama/ollama-entrypoint.sh
RUN chmod +x /ollama/ollama-entrypoint.sh

EXPOSE 11434
ENTRYPOINT ["/ollama/ollama-entrypoint.sh"]

