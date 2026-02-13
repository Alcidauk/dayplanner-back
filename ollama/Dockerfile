FROM ollama/ollama:latest

COPY ./ollama-entrypoint.sh /ollama/ollama-entrypoint.sh
RUN chmod +x /ollama/ollama-entrypoint.sh

EXPOSE 11434
ENTRYPOINT ["/ollama/ollama-entrypoint.sh"]

