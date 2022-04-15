#!/bin/bash

for f in ../build/contracts/*.json ;
do
cat $f | jq -j ".abi" > abi/$(basename ${f})
done