# nuitka-project: --mode=onefile
# nuitka-project: --lto=yes
# nuitka-project: --deployment
# nuitka-project: --output-dir=build
# nuitka-project: --assume-yes-for-downloads

# nuitka-project-if: {OS} == "Windows":
#   nuitka-project: --output-filename=CopilotProxy.exe
#   nuitka-project: --include-package=mitmproxy_windows

# nuitka-project-if: {OS} == "Darwin":
#   nuitka-project: --output-filename=CopilotProxy
#   nuitka-project: --macos-target-arch=arm64
#   nuitka-project: --macos-sign-identity=-

# nuitka-project-if: {OS} == "Linux":
#   nuitka-project: --output-filename=CopilotProxy
#   nuitka-project: --include-package=mitmproxy_linux


from main import run

run()
