#!/bin/bash
set -eu
: "${PROTOBUF_VERSION:=25.1}"

if [ -z "${PROTOC_EXE+x}" ]; then
	PROTOC_EXE="$(command -v protoc || true)"
fi
if [ -n "${PROTOC_EXE}" ]; then
	exit 0
fi
if [ ! -f protoc/bin/protoc ]; then
	curl -LO "https://github.com/protocolbuffers/protobuf/releases/download/v${PROTOBUF_VERSION}/protoc-${PROTOBUF_VERSION}-linux-x86_64.zip"
	unzip "protoc-${PROTOBUF_VERSION}-linux-x86_64.zip" -d protoc
	rm -f "protoc-${PROTOBUF_VERSION}-linux-x86_64.zip"
fi
