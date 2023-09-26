# Unity Project Version Management Command-line Interface (CLI)
Command-line interface utility for manipulating the project version of a Unity project.

```text
% unityprjver --help

usage: unityprjver [-h] [--build-number NUMBER] [--logging-level LEVEL] --path PATH [--replace-patch-version]
                   [--update-version]

Unreal Engine project version utility

options:
  -h, --help            show this help message and exit
  --build-number NUMBER
                        specify the build number of the Unreal Engine project
  --logging-level LEVEL
                        specify the logging level (critical, error, warning, info, debug)
  --path PATH           specify the path to the Unreal Engine project
  --replace-patch-version
                        indicate whether to replace the patch version of the Unreal Engine project with the specified
                        build number. This argument MUST be used with the argument `--build-number`.
  --update-version      indicate whether to update the defined in the Unreal Engine project. This argument MUST be
                        used with the argument `--build-number`.
```
