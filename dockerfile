FROM python:3.13.1

WORKDIR /app

COPY requirements.txt /app/
COPY . /app/

# Create and activate virtual environment
RUN python -m venv /app/.venv && \
    . /app/.venv/bin/activate && \
    pip install --no-cache-dir -qU -r requirements.txt

# Set the virtual environment activation in entrypoint
ENTRYPOINT ["/bin/bash", "-c", "source /app/.venv/bin/activate && exec \"$@\""]
CMD ["python", "app.py"]