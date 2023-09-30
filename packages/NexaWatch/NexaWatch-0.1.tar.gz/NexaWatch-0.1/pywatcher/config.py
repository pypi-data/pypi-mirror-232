# This LANGUAGES dictionary maps common file extensions or language identifiers 
# to their respective interpreters or execution commands.
# 
# By defining these mappings, we can easily support multiple programming languages
# for our file watcher utility. When a user specifies a particular language or file type,
# the corresponding interpreter or command is invoked to run the detected file.
# 
# HOW TO EXTEND:
# If you wish to add support for more languages or file types, simply add a new key-value 
# pair to this dictionary. The key should represent the file extension or a short identifier
# for the language, and the value should be the command or interpreter used to run files of that type.

LANGUAGES = {
    "py": "python",      # Python scripts are run using the 'python' command.
    "js": "node",        # JavaScript files are executed using the 'node' runtime.
    "rb": "ruby",        # Ruby scripts are run using the 'ruby' command.
    "php": "php",        # PHP scripts are run using the 'php' command.
    "sh": "bash",        # Shell scripts use 'bash' or an alternative shell.
    "pl": "perl",        # Perl scripts use the 'perl' command.
    "lua": "lua",        # Lua scripts are run using the 'lua' command.
    "go": "go run",      # Go files are executed using 'go run'.
    "rs": "cargo run",   # Rust files can be run with 'cargo run' if using Cargo.
    "java": "java",      # Java files are compiled and run using the 'java' command.
    "kt": "kotlin",      # Kotlin files are compiled and run using the 'kotlin' command.
    "swift": "swift",    # Swift files are compiled and run using the 'swift' command.
    "c": "gcc -o output && ./output",  # C files are compiled and run using gcc.
    "cpp": "g++ -o output && ./output",  # C++ files are compiled and run using g++.
    "cs": "dotnet run",  # C# files can be run with 'dotnet run' if using .NET Core.
    "dart": "dart",      # Dart files are run using the 'dart' command.
    "rs": "rustc -o output && ./output",  # Rust files are compiled and run using rustc.
    # Add more mappings here as needed.
    # ...
}
