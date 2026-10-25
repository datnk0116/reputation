#!/bin/sh
# Chạy trên máy của bạn (có internet) để tải dữ liệu vào data/
cd "$(dirname "$0")/data"
curl -O https://snap.stanford.edu/data/email-Eu-core.txt.gz
curl -O https://snap.stanford.edu/data/email-Eu-core-department-labels.txt.gz
