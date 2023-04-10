FROM ubuntu:latest

# Install basic packages
RUN apt update
RUN apt install -y openssl ca-certificates vim make gcc golang-go protobuf-compiler python3 netcat iputils-ping iproute2 python3-pip


# Set up certificates
ARG cert_location=/usr/local/share/ca-certificates
RUN mkdir -p ${cert_location}
# Get certificate from "github.com"
RUN openssl s_client -showcerts -connect github.com:443 </dev/null 2>/dev/null|openssl x509 -outform PEM > ${cert_location}/github.crt
# Update certificates
RUN update-ca-certificates

# Install python extensions for protoc
COPY src /project2/src
WORKDIR /project2/src
RUN pip install -r requirement.txt