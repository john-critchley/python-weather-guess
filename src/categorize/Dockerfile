FROM tensorflow/tensorflow:2.13.0

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Install extra Python deps
COPY src/categorize/requirements.txt /tmp/categorize-req.txt
RUN pip install --no-cache-dir -r /tmp/categorize-req.txt

# Install shared deps
COPY requirements.txt /tmp/root-req.txt
RUN pip install --no-cache-dir -r /tmp/root-req.txt

# Copy full source tree
COPY src /app/src

#-jc TEMP WORKAROUND: app uses CWD-relative model path.
#-jc Creates symlink so ../model/vgg19-weather.h5 resolves correctly.
#-jc Proper fix later: make path relative to __file__ in runtime/app.py
RUN ln -s /app/src/categorize/model /model

#-jc Ensure service uses its intended config inside container.
#-jc Without this the loader falls back to common defaults (127.0.0.1 bind).
ENV CONFIG_FILE=/app/src/categorize/config/default.ini

WORKDIR /app

EXPOSE 8081

CMD ["python", "src/categorize/runtime/app.py"]

