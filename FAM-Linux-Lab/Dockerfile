# FAM server -- offline Linux image build.
# All Python dependencies come from the local wheels/ directory; no network
# access is needed at build time.  The base images (python:3.12-slim and
# nginx:alpine) must already be present on the Docker host (saved with
# "docker save" on an authorized connected system).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Offline install of the pinned FAM requirements plus the certificate helper
# (used once by gen_cert.py to create the lab TLS certificate).
COPY wheels /tmp/wheels
COPY server/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --no-index --find-links=/tmp/wheels \
        -r /tmp/requirements.txt cryptography \
    && rm -rf /tmp/wheels

# The equipment probe runs the system OpenSSH client.  collect-ssh.sh copies
# the host client with its loader and libraries; run-ssh.sh executes it
# through that bundled loader, so the image's own C library is irrelevant.
COPY ssh-bundle /usr/local/fam-ssh
RUN if [ -f /usr/local/fam-ssh/run-ssh.sh ]; then \
        ln -sf /usr/local/fam-ssh/run-ssh.sh /usr/local/bin/ssh \
        && chmod 0755 /usr/local/fam-ssh/run-ssh.sh /usr/local/fam-ssh/ssh; \
    fi

# Application source: the same reviewed server package used on Windows.
COPY server /app/server
COPY gen_cert.py /app/gen_cert.py

EXPOSE 8765
CMD ["python", "server/app.py"]
