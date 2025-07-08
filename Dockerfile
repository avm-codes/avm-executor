FROM public.ecr.aws/lambda/python:3.12

RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt
COPY requirements.txt .

# Install the specified packages
RUN pip install -r requirements.txt

# Install tar (required for Node.js installation)
RUN microdnf install -y tar xz

# Install Node.js (latest LTS), npm, and npx
ENV NODE_VERSION=20.14.0
RUN curl -fsSL https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.xz -o node.tar.xz \
    && tar -xJf node.tar.xz -C /usr/local --strip-components=1 \
    && rm node.tar.xz \
    && node -v \
    && npm -v \
    && npx -v

# Copy function code
COPY lambda_function.py .
COPY app/ ./app/

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.handler" ]