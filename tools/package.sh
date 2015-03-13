#!/usr/bin/env bash
set -e

# create artifact
PRODUCT=client
FILENAME=${PRODUCT}-${BUILD_NUMBER}
mkdir -p artifact/${PRODUCT}
cp -R  README.md LICENSE bin cskcommands setup.py artifact/${PRODUCT}
cd artifact 
tar -czf ${FILENAME}.tar.gz ${PRODUCT}
find ${PRODUCT}/bin -type f -exec mv {} {}.py \;
tar -czf ${FILENAME}-win.tar.gz ${PRODUCT}
. ~/.awscreds
s3put -b builds.clearcodelabs.com --grant public-read --prefix ${PWD}/ ${FILENAME}.tar.gz
s3put -b builds.clearcodelabs.com --grant public-read --prefix ${PWD}/ ${FILENAME}-win.tar.gz
set +x
echo "[CCLARTIFACT:{\"name\": \"${PRODUCT}\", \"location\": \"https://s3.amazonaws.com/builds.clearcodelabs.com/${FILENAME}.tar.gz\"}]"
echo "[CCLARTIFACT:{\"name\": \"${PRODUCT}-win\", \"location\": \"https://s3.amazonaws.com/builds.clearcodelabs.com/${FILENAME}-win.tar.gz\"}]"
