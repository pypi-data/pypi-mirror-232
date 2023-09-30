#!/bin/bash

curl -L https://artifactdb.github.io/BiocObjectSchemas/bundle.tar.gz > bundle.tar.gz # for testing the latest.
#curl -L https://github.com/ArtifactDB/BiocObjectSchemas/releases/download/2023-09-28/bundle.tar.gz > bundle.tar.gz
rm -rf schemas
tar -xvf bundle.tar.gz

dest=../src/dolomite_schemas/schemas
rm -rf ${dest}
mv resolved ${dest}
