FROM ubuntu:latest

# Install basic packages
RUN apt update
RUN apt install -y openssl ca-certificates vim make gcc golang-go protobuf-compiler python3 netcat iputils-ping iproute2 python3-pip

# Set up certificates
ARG cert_location=/usr/local/share/ca-certificates
RUN mkdir -p ${cert_location}
# Get certificate from "github.com"
RUN openssl s_client -showcerts -connect github.com:443 </dev/null 2>/dev/null|openssl x509 -outform PEM > ${cert_location}/github.crt
# Get certificate from "proxy.golang.org"
RUN openssl s_client -showcerts -connect google.golang.org:443 </dev/null 2>/dev/null|openssl x509 -outform PEM >  ${cert_location}/google.golang.crt
# Update certificates
RUN update-ca-certificates

# Install go extensions for protoc
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
RUN go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
ENV PATH="$PATH:/root/go/bin"

# Install python extensions for protoc
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install grpcio
RUN python3 -m pip install grpcio-tools
COPY src /project1/src
WORKDIR /project1/src