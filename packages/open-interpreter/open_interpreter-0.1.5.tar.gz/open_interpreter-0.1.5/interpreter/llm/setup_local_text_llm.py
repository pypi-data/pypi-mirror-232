"""

This needs to be refactored. Prob replaced with GPT4ALL.

"""

import os
import sys
import appdirs
import traceback
import inquirer
import subprocess
from rich import print as rprint
from rich.markdown import Markdown
import os
import shutil
import tokentrim as tt
from huggingface_hub import list_files_info, hf_hub_download


def setup_local_text_llm(interpreter):

    DEFAULT_CONTEXT_WINDOW = 2000
    DEFAULT_MAX_TOKENS = 1000

    repo_id = interpreter.model.split("huggingface/")[1]

    if "TheBloke/CodeLlama-" not in repo_id:
      # ^ This means it was prob through the old --local, so we have already displayed this message.
      # Hacky. Not happy with this
      rprint('', Markdown(f"**Open Interpreter** will use `{repo_id}` for local execution. Use your arrow keys to set up the model."), '')

    raw_models = list_gguf_files(repo_id)
    
    if not raw_models:
        rprint(f"Failed. Are you sure there are GGUF files in `{repo_id}`?")
        return None

    combined_models = group_and_combine_splits(raw_models)

    selected_model = None

    # First we give them a simple small medium large option. If they want to see more, they can.

    if len(combined_models) > 3:

        # Display Small Medium Large options to user
        choices = [
            format_quality_choice(combined_models[0], "Small"),
            format_quality_choice(combined_models[len(combined_models) // 2], "Medium"),
            format_quality_choice(combined_models[-1], "Large"),
            "See More"
        ]
        questions = [inquirer.List('selected_model', message="Quality (smaller is faster, larger is more capable)", choices=choices)]
        answers = inquirer.prompt(questions)
        if answers["selected_model"].startswith("Small"):
            selected_model = combined_models[0]["filename"]
        elif answers["selected_model"].startswith("Medium"):
            selected_model = combined_models[len(combined_models) // 2]["filename"]
        elif answers["selected_model"].startswith("Large"):
            selected_model = combined_models[-1]["filename"]
    
    if selected_model == None:
        # This means they either selected See More,
        # Or the model only had 1 or 2 options

        # Display to user
        choices = [format_quality_choice(model) for model in combined_models]
        questions = [inquirer.List('selected_model', message="Quality (smaller is faster, larger is more capable)", choices=choices)]
        answers = inquirer.prompt(questions)
        for model in combined_models:
            if format_quality_choice(model) == answers["selected_model"]:
                selected_model = model["filename"]
                break

    # Third stage: GPU confirm
    if confirm_action("Use GPU? (Large models might crash on GPU, but will run more quickly)"):
      n_gpu_layers = -1
    else:
      n_gpu_layers = 0

    # Get user data directory
    user_data_dir = appdirs.user_data_dir("Open Interpreter")
    default_path = os.path.join(user_data_dir, "models")

    # Ensure the directory exists
    os.makedirs(default_path, exist_ok=True)

    # Define the directories to check
    directories_to_check = [
        default_path,
        "llama.cpp/models/",
        os.path.expanduser("~") + "/llama.cpp/models/",
        "/"
    ]

    # Check for the file in each directory
    for directory in directories_to_check:
        path = os.path.join(directory, selected_model)
        if os.path.exists(path):
            model_path = path
            break
    else:
        # If the file was not found, ask for confirmation to download it
        download_path = os.path.join(default_path, selected_model)
      
        rprint(f"This language model was not found on your system.\n\nDownload to `{default_path}`?", "")
        if confirm_action(""):
            for model_details in combined_models:
                if model_details["filename"] == selected_model:
                    selected_model_details = model_details

                    # Check disk space and exit if not enough
                    if not enough_disk_space(selected_model_details['Size'], default_path):
                        rprint(f"You do not have enough disk space available to download this model.")
                        return None

            # Check if model was originally split
            split_files = [model["filename"] for model in raw_models if selected_model in model["filename"]]
            
            if len(split_files) > 1:
                # Download splits
                for split_file in split_files:
                    # Do we already have a file split downloaded?
                    split_path = os.path.join(default_path, split_file)
                    if os.path.exists(split_path):
                        if not confirm_action(f"Split file {split_path} already exists. Download again?"):
                            continue
                    hf_hub_download(
                        repo_id=repo_id,
                        filename=split_file,
                        local_dir=default_path,
                        local_dir_use_symlinks=False,
                        resume_download=True)
                
                # Combine and delete splits
                actually_combine_files(default_path, selected_model, split_files)
            else:
                hf_hub_download(
                    repo_id=repo_id,
                    filename=selected_model,
                    local_dir=default_path,
                    local_dir_use_symlinks=False,
                    resume_download=True)

            model_path = download_path
        
        else:
            rprint('\n', "Download cancelled. Exiting.", '\n')
            return None

    # This is helpful for folks looking to delete corrupted ones and such
    rprint(Markdown(f"Model found at `{model_path}`"))
  
    try:
        from llama_cpp import Llama
    except:
        if interpreter.debug_mode:
            traceback.print_exc()
        # Ask for confirmation to install the required pip package
        message = "Local LLM interface package not found. Install `llama-cpp-python`?"
        if confirm_action(message):
            
            # We're going to build llama-cpp-python correctly for the system we're on

            import platform
            
            def check_command(command):
                try:
                    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    return True
                except subprocess.CalledProcessError:
                    return False
                except FileNotFoundError:
                    return False
            
            def install_llama(backend):
                env_vars = {
                    "FORCE_CMAKE": "1"
                }
                
                if backend == "cuBLAS":
                    env_vars["CMAKE_ARGS"] = "-DLLAMA_CUBLAS=on"
                elif backend == "hipBLAS":
                    env_vars["CMAKE_ARGS"] = "-DLLAMA_HIPBLAS=on"
                elif backend == "Metal":
                    env_vars["CMAKE_ARGS"] = "-DLLAMA_METAL=on"
                else:  # Default to OpenBLAS
                    env_vars["CMAKE_ARGS"] = "-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"
                
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "llama-cpp-python"], env={**os.environ, **env_vars}, check=True)
                except subprocess.CalledProcessError as e:
                    rprint(f"Error during installation with {backend}: {e}")
            
            def supports_metal():
                # Check for macOS version
                if platform.system() == "Darwin":
                    mac_version = tuple(map(int, platform.mac_ver()[0].split('.')))
                    # Metal requires macOS 10.11 or later
                    if mac_version >= (10, 11):
                        return True
                return False
            
            # Check system capabilities
            if check_command(["nvidia-smi"]):
                install_llama("cuBLAS")
            elif check_command(["rocminfo"]):
                install_llama("hipBLAS")
            elif supports_metal():
                install_llama("Metal")
            else:
                install_llama("OpenBLAS")
          
            from llama_cpp import Llama
            rprint('', Markdown("Finished downloading `Code-Llama` interface."), '')

            # Tell them if their architecture won't work well

            # Check if on macOS
            if platform.system() == "Darwin":
                # Check if it's Apple Silicon
                if platform.machine() != "arm64":
                    print("Warning: You are using Apple Silicon (M1/M2) Mac but your Python is not of 'arm64' architecture.")
                    print("The llama.ccp x86 version will be 10x slower on Apple Silicon (M1/M2) Mac.")
                    print("\nTo install the correct version of Python that supports 'arm64' architecture:")
                    print("1. Download Miniforge for M1/M2:")
                    print("wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh")
                    print("2. Install it:")
                    print("bash Miniforge3-MacOSX-arm64.sh")
                    print("")
      
        else:
            rprint('', "Installation cancelled. Exiting.", '')
            return None

    # Initialize and return Code-Llama
    assert os.path.isfile(model_path)
    params = {
        'model_path': model_path,
        'n_gpu_layers': n_gpu_layers,
        'verbose': interpreter.debug_mode
    }
    if interpreter.context_window:
        params['n_ctx'] = interpreter.context_window
    else:
        params['n_ctx'] = DEFAULT_CONTEXT_WINDOW
    llama_2 = Llama(**params)

    def local_text_llm(messages):
        """
        Returns a generator
        """

        system_message = messages[0]["content"]
        messages = messages[1:]

        if interpreter.context_window:
            context_window = interpreter.context_window
        else:
            context_window = DEFAULT_CONTEXT_WINDOW

        if interpreter.max_tokens:
            max_tokens = interpreter.max_tokens
        else:
            max_tokens = DEFAULT_MAX_TOKENS
        

        messages = tt.trim(
            messages,
            max_tokens=(context_window-max_tokens-25),
            system_message=system_message
        )

        prompt = messages_to_prompt(messages, interpreter.model)
        # Lmao i can't believe this works (it does need this btw)
        if messages[-1]["role"] != "function":
            if messages[-1]["content"].lower() not in ["hello", "hi", "hey", "helo", "hii"]: # :)
                prompt += """Let's explore this. By the way, I can run code on your machine by writing the code in a markdown code block. This works if I put a newline after ```shell, ```javascript, ```python, ```R, and ```applescript then write code. I'm going to try to do this for your task, and I'll put the *correct* language after the "```" now. Anyway, """
        elif messages[-1]["role"] == "function" and messages[-1]["content"] != "No output":
            prompt += "Given the output of the code I just ran, "
        elif messages[-1]["role"] == "function" and messages[-1]["content"] == "No output":
            prompt += "Given the fact that the code I just ran produced no output, "

        if interpreter.debug_mode:
            print("Prompt:", prompt)

        first_token = True

        for chunk in llama_2(
                prompt=prompt,
                stream=True,
                temperature=interpreter.temperature,
                stop=["</s>"],
                max_tokens=max_tokens
            ):

            # Get generated content
            content = chunk["choices"][0]["text"]

            # Add delta for OpenAI compatability
            chunk["choices"][0]["delta"] = {}

            if first_token:
                # Don't capitalize or anything if it's just a space first
                if content.strip() != "":
                    first_token = False
                    # This is the first chunk. We'll need to capitalize it, because our prompt ends in a ", "
                    content = content.capitalize()
                    
                    # We'll also need to yield "role: assistant" for OpenAI compatability. 
                    # CodeLlama will not generate this
                    chunk["choices"][0]["delta"]["role"] = "assistant"

            # Put content into a delta for OpenAI compatability.
            chunk["choices"][0]["delta"]["content"] = content

            yield chunk
      
    return local_text_llm

def messages_to_prompt(messages, model):

        for message in messages:
          # Happens if it immediatly writes code
          if "role" not in message:
            message["role"] = "assistant"

        # Falcon prompt template
        if "falcon" in model.lower():

          formatted_messages = ""
          for message in messages:
            formatted_messages += f"{message['role'].capitalize()}: {message['content']}\n"

            if "function_call" in message and "parsed_arguments" in message['function_call']:
                if "code" in message['function_call']['parsed_arguments'] and "language" in message['function_call']['parsed_arguments']:
                    code = message['function_call']['parsed_arguments']["code"]
                    language = message['function_call']['parsed_arguments']["language"]
                    formatted_messages += f"\n```{language}\n{code}\n```"

          formatted_messages = formatted_messages.strip()

        else:
          # Llama prompt template

          # Extracting the system prompt and initializing the formatted string with it.
          system_prompt = messages[0]['content']
          formatted_messages = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n"

          # Loop starting from the first user message
          for index, item in enumerate(messages[1:]):
              role = item['role']
              content = item['content']

              if role == 'user':
                  formatted_messages += f"{content} [/INST] "
              elif role == 'function':
                  formatted_messages += f"Output: {content} [/INST] "
              elif role == 'assistant':
                    formatted_messages += content

                    # Add code
                    if "function_call" in item and "parsed_arguments" in item['function_call']:
                        if "code" in item['function_call']['parsed_arguments'] and "language" in item['function_call']['parsed_arguments']:
                            code = item['function_call']['parsed_arguments']["code"]
                            language = item['function_call']['parsed_arguments']["language"]
                            formatted_messages += f"\n```{language}\n{code}\n```"

                    formatted_messages += " </s><s>[INST] "


          # Remove the trailing '<s>[INST] ' from the final output
          if formatted_messages.endswith("<s>[INST] "):
              formatted_messages = formatted_messages[:-10]

        return formatted_messages


def confirm_action(message):
    question = [
        inquirer.Confirm('confirm',
                         message=message,
                         default=True),
    ]

    answers = inquirer.prompt(question)
    return answers['confirm']



import os
import inquirer
from huggingface_hub import list_files_info, hf_hub_download, login
from typing import Dict, List, Union

def list_gguf_files(repo_id: str) -> List[Dict[str, Union[str, float]]]:
    """
    Fetch all files from a given repository on Hugging Face Model Hub that contain 'gguf'.

    :param repo_id: Repository ID on Hugging Face Model Hub.
    :return: A list of dictionaries, each dictionary containing filename, size, and RAM usage of a model.
    """

    try:
      files_info = list_files_info(repo_id=repo_id)
    except Exception as e:
      if "authentication" in str(e).lower():
        print("You likely need to be logged in to HuggingFace to access this language model.")
        print(f"Visit this URL to log in and apply for access to this language model: https://huggingface.co/{repo_id}")
        print("Then, log in here:")
        login()
        files_info = list_files_info(repo_id=repo_id)
  
    gguf_files = [file for file in files_info if "gguf" in file.rfilename]

    gguf_files = sorted(gguf_files, key=lambda x: x.size)

    # Prepare the result
    result = []
    for file in gguf_files:
        size_in_gb = file.size / (1024**3)
        filename = file.rfilename
        result.append({
            "filename": filename,
            "Size": size_in_gb,
            "RAM": size_in_gb + 2.5,
        })

    return result

from typing import List, Dict, Union

def group_and_combine_splits(models: List[Dict[str, Union[str, float]]]) -> List[Dict[str, Union[str, float]]]:
    """
    Groups filenames based on their base names and combines the sizes and RAM requirements.

    :param models: List of model details.
    :return: A list of combined model details.
    """
    grouped_files = {}

    for model in models:
        base_name = model["filename"].split('-split-')[0]
        
        if base_name in grouped_files:
            grouped_files[base_name]["Size"] += model["Size"]
            grouped_files[base_name]["RAM"] += model["RAM"]
            grouped_files[base_name]["SPLITS"].append(model["filename"])
        else:
            grouped_files[base_name] = {
                "filename": base_name,
                "Size": model["Size"],
                "RAM": model["RAM"],
                "SPLITS": [model["filename"]]
            }

    return list(grouped_files.values())


def actually_combine_files(default_path: str, base_name: str, files: List[str]) -> None:
    """
    Combines files together and deletes the original split files.

    :param base_name: The base name for the combined file.
    :param files: List of files to be combined.
    """
    files.sort()    
    base_path = os.path.join(default_path, base_name)
    with open(base_path, 'wb') as outfile:
        for file in files:
            file_path = os.path.join(default_path, file)
            with open(file_path, 'rb') as infile:
                outfile.write(infile.read())
            os.remove(file_path)

def format_quality_choice(model, name_override = None) -> str:
    """
    Formats the model choice for display in the inquirer prompt.
    """
    if name_override:
        name = name_override
    else:
        name = model['filename']
    return f"{name} | Size: {model['Size']:.1f} GB, Estimated RAM usage: {model['RAM']:.1f} GB"

def enough_disk_space(size, path) -> bool:
    """
    Checks the disk to verify there is enough space to download the model.

    :param size: The file size of the model.
    """
    _, _, free = shutil.disk_usage(path)

    # Convert bytes to gigabytes
    free_gb = free / (2**30) 

    if free_gb > size:
        return True

    return False
