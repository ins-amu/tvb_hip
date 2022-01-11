#!/bin/bash

for i in 1 2 3
do
docker build -t hip:stage$i -f stage$i.dockerfile .
done
