#!/bin/bash
set -e

# Fonction pour vérifier si le serveur Ollama est prêt
wait_for_ollama() {
    echo "Waiting for Ollama server to start..."
    while ! curl -s http://localhost:11434/v1/models >/dev/null 2>&1; do
        sleep 1
    done
    echo "Ollama server started."
}

# Lancer Ollama en arrière-plan et rediriger les logs vers stdout
ollama serve > /proc/1/fd/1 2>/proc/1/fd/2 &

# Attendre que le serveur soit prêt
wait_for_ollama

# Vérifier si le modèle llama2 existe déjà
if ! ollama list | grep -q llama3.2; then
    echo "Pulling llama2 model..."
    # Pull avec logs en direct
    ollama pull llama3.2 | tee /proc/1/fd/1
    echo "llama3.2 model pulled successfully."
else
    echo "llama3.2 model is installed"
fi

# Garder le serveur Ollama actif
wait

