#!/usr/bin/env bash
set -euo pipefail

APP_NAME="个人计算机知识库"
BUNDLE_ID="com.qiuxiuhao.computerknowledgeapp"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ICON_PATH="${PROJECT_ROOT}/assets/app_icon.icns"
ENTRYPOINT="${PROJECT_ROOT}/src/main.py"
APP_PATH="${PROJECT_ROOT}/dist/${APP_NAME}.app"

cd "${PROJECT_ROOT}"

if [[ ! -f "${ICON_PATH}" ]]; then
    echo "Missing app icon: ${ICON_PATH}" >&2
    exit 1
fi

if ! python -m PyInstaller --version >/dev/null 2>&1; then
    echo "PyInstaller is not installed in the current Python environment." >&2
    echo "Install it with: python -m pip install pyinstaller" >&2
    exit 1
fi

echo "Cleaning previous build outputs..."
rm -rf "${PROJECT_ROOT}/build" "${PROJECT_ROOT}/dist"

echo "Building ${APP_NAME}.app..."
python -m PyInstaller \
    --noconfirm \
    --windowed \
    --name "${APP_NAME}" \
    --icon "${ICON_PATH}" \
    --osx-bundle-identifier "${BUNDLE_ID}" \
    "${ENTRYPOINT}"

if [[ ! -d "${APP_PATH}" ]]; then
    echo "Build failed: ${APP_PATH} was not created." >&2
    exit 1
fi

bundled_database="$(
    find "${APP_PATH}" -type f \
        \( -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3" \) \
        -print -quit
)"

if [[ -n "${bundled_database}" ]]; then
    echo "Build failed: database file was bundled into the .app:" >&2
    echo "${bundled_database}" >&2
    exit 1
fi

echo "Build complete: ${APP_PATH}"
echo "User data remains outside the app bundle:"
echo "${HOME}/Library/Application Support/computer_knowledge_app/knowledge.db"
