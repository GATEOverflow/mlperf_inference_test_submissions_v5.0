#!/bin/bash

if [ ! -e docs ]; then
    git clone https://github.com/GATEOverflow/inference_results_visualization_template.git docs
    test $? -eq 0 || exit $?
fi

python3 -m pip install -r docs/requirements.txt

if [ ! -e overrides ]; then
    cp -r docs/overrides overrides
    test $? -eq 0 || exit $?
fi

repo_owner=${INFERENCE_RESULTS_REPO_OWNER:-mlcommons}
repo_branch=${INFERENCE_RESULTS_REPO_BRANCH:-main}
repo_name=${INFERENCE_RESULTS_REPO_NAME:-inference_results_${INFERENCE_RESULTS_VERSION}}
ver_num=$(cat dbversion)
let ver_num++

if [ ! -e docs/javascripts/config.js ]; then
    if [ -n "${INFERENCE_RESULTS_VERSION}" ]; then
         echo "const results_version=\"${INFERENCE_RESULTS_VERSION}\";" > docs/javascripts/config.js;
         echo "var repo_owner=\"${repo_owner}\";" >> docs/javascripts/config.js;
         echo "var repo_branch=\"${repo_branch}\";" >> docs/javascripts/config.js;
         echo "var repo_name=\"${repo_name}\";" >> docs/javascripts/config.js;
         #ver_num=`echo ${INFERENCE_RESULTS_VERSION} | tr -cd '0-9'`
         echo "const dbVersion =\"${ver_num}\";" >> docs/javascripts/config.js;
    else
       echo "Please export INFERENCE_RESULTS_VERSION=v4.1 or the corresponding version";
       exit 1
    fi
fi

if [ ! -e docs/thirdparty/tablesorter ]; then
    cd docs/thirdparty && git clone https://github.com/Mottie/tablesorter.git && cd -
    test $? -eq 0 || exit $?
fi

if [ ! -e process_results_table.py ]; then
    cp docs/process_results_table.py .
    test $? -eq 0 || exit $?
fi

if [ ! -e process.py ]; then
    cp docs/process.py .
    test $? -eq 0 || exit $?
fi

python3 process.py
test $? -eq 0 || exit $?
python3 process_results_table.py
test $? -eq 0 || exit $?
