FROM python:3.12-slim

WORKDIR /app

# Copy all application and backend code
COPY . /app

# Ensure Python output is sent straight to terminal (unbuffered)
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

# Start WishCue AI Backend server
CMD ["python", "-u", "backend/app.py"]
