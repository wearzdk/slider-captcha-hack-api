FROM thehale/python-poetry
# Your build steps here.
# RUN apt-get update && apt-get install libgl1 -y
ENV FASTAPI_ENV=production
ENV SLIDER_CAPTCHA_KEY=
WORKDIR /app
COPY . /app/
RUN poetry install --only main --no-interaction
EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "slider_captcha.api:app", "--host", "0.0.0.0", "--port", "8000"]

