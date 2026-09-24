FROM python:3.11-slim

# Crear usuario estándar para compatibilidad total con Hugging Face Spaces (UID 1000)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PORT=7860 \
    HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1

WORKDIR $HOME/app

# Instalar dependencias Python
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y el frontend preconstruido (lab/dist)
COPY --chown=user:user . .

EXPOSE 7860

CMD ["python", "server.py"]
