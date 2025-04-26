"""
helpers.py

Utility functions and helper classes used throughout the application.
Includes:
- File operations (JSON read/write)
- Directory and template setup
- Markdown processing
- Dynamic module import
- Terminal launching
"""

import json
import os
import platform
import shutil
import importlib
import logging
import sys
import re
import subprocess
import shlex
import threading
import markdown


def ensure_directories_exist(paths: list[str]) -> None:
    """
    Ensure that a list of directories exists. Creates them if missing.

    Args:
        paths (list[str]): List of directory paths to create.
    """
    for dir_path in paths:
        os.makedirs(dir_path, exist_ok=True)


def ensure_default_json_files(template_dir: str, target_dir: str) -> None:
    """
    Copy default JSON files from template_dir to target_dir if they don't already exist.

    Args:
        template_dir (str): Source directory containing template JSON files.
        target_dir (str): Destination directory for user-specific JSON files.
    """
    for filename in os.listdir(template_dir):
        if filename.endswith('.json'):
            src = os.path.join(template_dir, filename)
            dst = os.path.join(target_dir, filename)
            if not os.path.exists(dst):
                shutil.copy(src, dst)


def open_path(path: str) -> None:
    """
    Open a file or folder in the system file explorer.

    Args:
        path (str): Path to file or directory.
    """
    logging.info(f"Opening path in file explorer: {path}")
    system = platform.system()
    command = {
        'Windows': f'start "" "{path}"',
        'Darwin': f'open "{path}"',
    }.get(system, f'xdg-open "{path}"')
    os.system(command)


def import_from_path(module_name: str, file_path: str):
    """
    Dynamically import a module or package given an absolute file path.

    Args:
        module_name (str): Name to assign the imported module.
        file_path (str): Path to the module file or package directory.

    Returns:
        module: Imported Python module.
    """
    file_path = os.path.abspath(file_path)
    logging.debug(f"Importing module '{module_name}' from '{file_path}'")

    if os.path.isdir(file_path):
        init_path = os.path.join(file_path, '__init__.py')
        if not os.path.isfile(init_path):
            logging.debug(f"Missing __init__.py in directory: {file_path}")
            raise ImportError(f"Directory '{file_path}' is not a valid package (missing __init__.py)")
        file_path = init_path

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        logging.debug(f"Failed to create import spec for {file_path}")
        raise ImportError(f"Can't find module at {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    logging.debug(f"Module '{module_name}' imported successfully")
    return module


def md_to_plain(content: str) -> str:
    """
    Convert Markdown-formatted text to plain text.

    Args:
        content (str): Markdown string.

    Returns:
        str: Plain text representation of the input.
    """
    content = re.sub(r'^.*!\[.*?\]\(.*?\).*\n?', '', content, flags=re.MULTILINE)
    content = re.sub(r'#{1,6}\s*', '', content)
    content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
    content = re.sub(r'\*([^*]+)\*', r'\1', content)
    content = re.sub(r'__([^_]+)__', r'\1', content)
    content = re.sub(r'_([^_]+)_', r'\1', content)
    content = re.sub(r'^\s*[-*]\s+', '- ', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*\d+\.\s+', lambda m: m.group(), content, flags=re.MULTILINE)
    content = re.sub(r'`([^`]+)`', r'\1', content)
    content = re.sub(r'\n{2,}', '\n\n', content)
    return content


def md_to_html(content: str, base_path: str = "") -> str:
    """
    Convert markdown content into styled HTML with optional base path for images.
    """
    # Fix image paths if a base path is provided
    if base_path:
        def fix_image_paths(match):
            alt_text = match.group(1)
            img_path = match.group(2)
            # Convert to absolute path if relative
            if not img_path.startswith(('http://', 'https://', 'file://')):
                abs_path = os.path.abspath(os.path.join(base_path, img_path)).replace('\\', '/')
                return f'![{alt_text}](file:///{abs_path})'
            return match.group(0)
        content = re.sub(r'!\[(.*?)\]\((.*?)\)', fix_image_paths, content)


    # Then convert to HTML as before...
    styled_html = f"""
    <html>
    <head>
        <style>
            body {{ font-weight: 300; }}
            h1, h2, h3, h4, h5, h6 {{ font-weight: 400; border-bottom: 1px solid #eaecef; padding-bottom: 4px; }}
            pre {{ padding: 10px; border-radius: 5px; font-family: 'Consolas', monospace; }}
            code {{ font-family: 'Consolas', monospace; padding: 2px 4px; border-radius: 3px; }}
            blockquote {{ border-left: 4px solid #d0d7de; padding-left: 10px; margin-left: 0; }}
            a {{ text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            ul, ol {{ padding-left: 20px; }}
            img {{ max-width: 100%; height: auto; margin: 10px 0; }}
        </style>
    </head>
    <body>{markdown.markdown(content)}</body>
    </html>
    """
    return styled_html


def launch_python_shell():
    """
    Launch a new terminal window with an embedded shell,
    pre-configured with the current Python path and a custom prompt.
    """

    def _launch():
        custom_prompt = "(*** Netmig ***)"
        python_exe = sys.executable.replace("pythonw.exe",
                                            "python.exe") if platform.system() == "Windows" else sys.executable
        python_dir = os.path.dirname(python_exe)
        is_windows = platform.system() == "Windows"

        if is_windows:
            window_title = "Netmig Prompt"
            cmd = (
                f'start "{window_title}" cmd.exe /k '
                f'"title {window_title} && set PATH={python_dir};%PATH% && prompt {custom_prompt} $G"'
            )
        elif platform.system() == "Darwin":
            cmd = (
                f'osascript -e \'tell application "Terminal" to do script '
                f'"export PATH=\\"{python_dir}:$PATH\\"; export PS1=\\"{custom_prompt} $\\"; exec bash"\''
            )
        else:
            terminals = ["gnome-terminal", "konsole", "xfce4-terminal", "x-terminal-emulator"]
            for term in terminals:
                if shutil.which(term):
                    cmd = (
                        f'{term} -- bash -c '
                        f'"export PATH=\\"{python_dir}:$PATH\\"; export PS1=\\"{custom_prompt} $\\"; exec bash"'
                    )
                    break
            else:
                cmd = f'bash -c "export PATH=\\"{python_dir}:$PATH\\"; export PS1=\\"{custom_prompt} $\\"; exec bash"'

        logging.info("Launching Netmig Prompt")
        os.system(cmd)

    threading.Thread(target=_launch, daemon=True).start()


def clear_modules(pattern: str) -> None:
    """
    Clear cached Python modules matching a regex pattern and reload UI module.

    Args:
        pattern (str): Regex pattern to match module names.
    """
    logging.debug(f"Clearing modules matching pattern: {pattern}")
    count = 0
    for module in list(sys.modules):
        if re.search(f'^{pattern}\.\S+', module):
            sys.modules.pop(module)
            count += 1
    importlib.reload(sys.modules['ui'])
    logging.debug("Reloaded 'ui' module")


def build_script_registry(script_dir: str) -> dict:
    """
    Build a registry of script metadata from a directory of script modules.

    Args:
        script_dir (str): Path to script modules folder.

    Returns:
        dict: Dictionary of metadata indexed by generated module ID.
    """
    logging.debug(f"Building script registry from: {script_dir}")
    script_registry = {}
    for name in os.listdir(script_dir):
        module = os.path.join(script_dir, name)
        if not os.path.isdir(module):
            continue

        meta_path = os.path.join(module, '__meta__')

        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r') as f:
                    script_info = json.load(f)
                    script_id = script_info.get("uuid")
                    script_registry[script_id] = script_info
                    script_registry[script_id]["module"] = module
                    logging.debug(f"Loaded metadata for module: {script_id}")
            except json.JSONDecodeError as e:
                logging.warning(f"Failed to load {meta_path}: {e}")
    logging.debug(f"Registry built with {len(script_registry)} scripts")
    return script_registry
