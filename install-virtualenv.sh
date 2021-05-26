#!/bin/bash

PYTHON='python'
DEPS="-r ${1-requirements.txt}"
WHEEL_DIR=$HOME/.pip/wheelhouse

LOCAL_ENV_PATH=local.virtualenv

rm -rf ${LOCAL_ENV_PATH}
${PYTHON} -m venv ${LOCAL_ENV_PATH}
"${LOCAL_ENV_PATH}/bin/pip" install --upgrade setuptools pip wheel

cat > "${LOCAL_ENV_PATH}/pip.conf" <<EOL
[wheel]
find-links = file://$WHEEL_DIR

[install]
find-links = file://$WHEEL_DIR
EOL

"${LOCAL_ENV_PATH}/bin/pip" wheel $DEPS --wheel-dir "${WHEEL_DIR}"
"${LOCAL_ENV_PATH}/bin/pip" install $DEPS
