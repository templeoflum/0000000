import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import openai
import requests
import os
from dotenv import load_dotenv
import yaml
import json
import threading
import logging

###############################################################################
# 1) Load Environment Variables and Configure API Keys
###############################################################################

# Configure logging
logging.basicConfig(
    filename='app.log',                    # Log file name
    filemode='a',                          # Append mode
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    level=logging.DEBUG                    # Logging level
)

def load_api_keys():
    """
    Loads API keys from the .env file.
    """
    try:
        load_dotenv()  # Load environment variables from .env
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        
        if not OPENAI_API_KEY or not GEMINI_API_KEY:
            raise ValueError("Could not find OPENAI_API_KEY or GEMINI_API_KEY in .env file.")
        
        openai.api_key = OPENAI_API_KEY  # Set OpenAI API key
        logging.info("Environment variables loaded successfully.")
        return OPENAI_API_KEY, GEMINI_API_KEY
    except Exception as e:
        logging.error(f"Error loading environment variables: {e}")
        messagebox.showerror("Error", f"Error loading environment variables: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

###############################################################################
# 2) Parsing Helpers: YAML / JSON / Markdown
###############################################################################

def parse_yaml(content: str) -> dict:
    """
    Parses YAML content into a Python dictionary.
    """
    try:
        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            raise ValueError("YAML content must be a dictionary at the top level.")
        return data
    except yaml.YAMLError as e:
        raise ValueError(f"YAML Parsing Error: {e}")

def parse_json(content: str) -> dict:
    """
    Parses JSON content into a Python dictionary.
    """
    try:
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError("JSON content must be a dictionary at the top level.")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON Parsing Error: {e}")

def parse_markdown(content: str) -> dict:
    """
    Minimal placeholder parser for Markdown.
    Stores the entire Markdown as a single field under Framework -> Content.
    """
    return {
        "Framework": {
            "Title": "Imported Markdown",
            "Content": content
        }
    }

def detect_format(file_path: str) -> str:
    """
    Detects the file format based on its extension.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if ext in (".yaml", ".yml"):
        return "YAML"
    elif ext == ".json":
        return "JSON"
    elif ext == ".md":
        return "Markdown"
    else:
        return ""

def parse_content(content: str, format_type: str) -> dict:
    """
    Parses content based on the detected or selected format.
    """
    if format_type == "YAML":
        return parse_yaml(content)
    elif format_type == "JSON":
        return parse_json(content)
    elif format_type == "Markdown":
        return parse_markdown(content)
    else:
        raise ValueError("Unsupported format.")

###############################################################################
# 3) AI Model Call Helpers
###############################################################################

def call_openai(prompt: str) -> str:
    """
    Calls OpenAI GPT-4 with the given prompt and returns the response.
    """
    logging.debug(f"Calling OpenAI GPT-4 with prompt: {prompt}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.7
        )
        expanded_text = response.choices[0].message.content.strip()
        logging.info("OpenAI GPT-4 response received successfully.")
        return expanded_text
    except Exception as e:
        logging.error(f"OpenAI API Error: {e}")
        return f"OpenAI API Error: {e}"

def call_gemini(prompt: str, gemini_api_key: str) -> str:
    """
    Calls Google Gemini 1.5 Flash model via REST API with the given prompt and returns the response.
    """
    logging.debug(f"Calling Gemini 1.5 Flash with prompt: {prompt}")
    GEMINI_API_URL = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-1.5-flash:generateContent"
    )
    headers = {"Content-Type": "application/json"}
    params = {"key": gemini_api_key}
    data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data)
        if response.status_code == 200:
            result = response.json()
            expanded_text = ""
            for cblock in result.get("results", []):
                for part in cblock.get("contents", []):
                    expanded_text += part.get("parts", [{}])[0].get("text", "")
            logging.info("Gemini 1.5 Flash response received successfully.")
            return expanded_text.strip()
        else:
            error_message = f"Gemini API Error {response.status_code}: {response.text}"
            logging.error(error_message)
            return error_message
    except Exception as e:
        logging.error(f"Gemini API Error: {e}")
        return f"Gemini API Error: {e}"

def call_model(model_name: str, prompt: str, gemini_api_key: str) -> str:
    """
    Routes the prompt to the selected AI model and returns the response.
    """
    if model_name == "OpenAI GPT-4":
        return call_openai(prompt)
    elif model_name == "Gemini 1.5 Flash":
        return call_gemini(prompt, gemini_api_key)
    else:
        return "Unsupported model."

###############################################################################
# 4) Expansion Logic (Matching the 'Framework' Structure)
###############################################################################

def expand_top_level(framework_dict: dict, model_name: str, gemini_api_key: str) -> dict:
    """
    Iterates over known keys in the 'Framework' dict,
    calls AI to expand them, and returns the updated dictionary.
    """
    expanded_framework = dict(framework_dict)  # Shallow copy

    # Expand textual lists (e.g., Vision, Inspiration, Conclusion, etc.)
    for key in [
        "Vision",
        "Inspiration",
        "Core_Principles",
        "Tools",
        "Methods",
        "Conclusion",
    ]:
        if key in framework_dict:
            original_content = framework_dict[key]
            # Convert list content to JSON string for clarity in the prompt
            prompt_content = json.dumps(original_content, indent=2)
            prompt = (
                f"Expand the following {key} for the framework:\n\n{prompt_content}\n\n"
                "Please provide a more detailed and enriched version."
            )
            expanded_text = call_model(model_name, prompt, gemini_api_key)
            # Store as a list item
            expanded_framework[key] = [expanded_text]

    # Expand 'Phases' if present and is a list of dictionaries
    if "Phases" in framework_dict and isinstance(framework_dict["Phases"], list):
        expanded_phases = []
        for phase in framework_dict["Phases"]:
            expanded_phase = dict(phase)  # Shallow copy
            phase_name = phase.get("Phase_Name", "Untitled Phase")
            phase_purpose = phase.get("Purpose", "")
            actions = phase.get("Actions", [])

            # Expand the phase purpose
            if phase_purpose:
                p_prompt = (
                    f"Expand the purpose of this phase:\n\n"
                    f"Phase Name: {phase_name}\n"
                    f"Purpose:\n{phase_purpose}\n\n"
                    "Provide more context, depth, and clarity."
                )
                expanded_purpose = call_model(model_name, p_prompt, gemini_api_key)
                expanded_phase["Purpose"] = expanded_purpose

            # Expand each action
            if actions and isinstance(actions, list):
                expanded_actions = []
                for action in actions:
                    a_prompt = (
                        f"Expand the following action from '{phase_name}':\n\n"
                        f"Action:\n{action}\n\n"
                        "Please provide more detail with relevant considerations."
                    )
                    expanded_action = call_model(model_name, a_prompt, gemini_api_key)
                    expanded_actions.append(expanded_action)
                expanded_phase["Actions"] = expanded_actions

            expanded_phases.append(expanded_phase)
        expanded_framework["Phases"] = expanded_phases

    return expanded_framework

###############################################################################
# 5) Converters (Back to YAML, JSON, or Minimal Markdown)
###############################################################################

def convert_to_markdown(data: dict) -> str:
    """
    Converts the expanded data structure back into a simple Markdown format.
    Expects top-level "Framework" key with subkeys like Title, Vision, Phases, etc.
    """
    framework = data.get("Framework", {})
    lines = []
    try:
        # Title + Metadata
        title = framework.get("Title", "Untitled Framework")
        lines.append(f"# {title}\n")

        metadata = framework.get("Metadata", {})
        for key, value in metadata.items():
            lines.append(f"**{key}:** {value}")
        lines.append("")  # Add a newline

        # Expand known fields
        for key in [
            "Vision",
            "Inspiration",
            "Core_Principles",
            "Tools",
            "Methods",
            "Conclusion",
        ]:
            if key in framework:
                lines.append(f"## {key}")
                content_list = framework[key]
                if isinstance(content_list, list):
                    for item in content_list:
                        lines.append(f"- {item}")
                else:
                    lines.append(f"- {str(content_list)}")
                lines.append("")

        # Phases
        if "Phases" in framework:
            lines.append("## Phases\n")
            for idx, phase in enumerate(framework["Phases"], 1):
                name = phase.get("Phase_Name", f"Phase {idx}")
                purpose = phase.get("Purpose", "")
                actions = phase.get("Actions", [])

                lines.append(f"### {name}\n")
                lines.append(f"**Purpose:** {purpose}\n")
                if actions:
                    lines.append("**Actions:**")
                    for i, act in enumerate(actions, 1):
                        lines.append(f"{i}. {act}")
                lines.append("")
    except Exception as e:
        return f"Markdown Conversion Error: {e}"

    return "\n".join(lines)

###############################################################################
# 6) The Main Expansion Process
###############################################################################

def expand_framework_in_thread(data: dict, model_choice: str, format_type: str, gemini_api_key: str):
    """
    Runs in a separate thread to avoid freezing the GUI.
    Expands the framework's fields, then converts back to the desired format.
    """
    try:
        if "Framework" not in data:
            messagebox.showerror(
                "Error",
                "No 'Framework' key found in the top-level dictionary. "
                "Please ensure your YAML/JSON has a top-level 'Framework' node."
            )
            logging.error("No 'Framework' key found in the input data.")
            return

        framework_dict = data["Framework"]
        logging.info("Starting expansion of the framework.")

        # Expand the top-level structure
        expanded_structure = expand_top_level(framework_dict, model_choice, gemini_api_key)

        # Overwrite the data structure with the expanded version
        data["Framework"] = expanded_structure

        # Convert back to chosen format
        if format_type == "YAML":
            output = yaml.dump(data, sort_keys=False, allow_unicode=True)
        elif format_type == "JSON":
            output = json.dumps(data, indent=2, ensure_ascii=False)
        elif format_type == "Markdown":
            output = convert_to_markdown(data)
        else:
            output = "Unsupported format."

        # Update the result box
        result_box.config(state=tk.NORMAL)
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, output)
        result_box.config(state=tk.DISABLED)

        logging.info("Framework expansion completed successfully.")

    except Exception as e:
        messagebox.showerror("Error", f"Expansion Failed: {e}")
        logging.error(f"Expansion Failed: {e}")

###############################################################################
# 7) GUI Code
###############################################################################

def upload_file_gui(format_var: tk.StringVar):
    """
    Handles the file upload process within the GUI.
    """
    filetypes = [
        ("YAML files", "*.yaml *.yml"),
        ("JSON files", "*.json"),
        ("Markdown files", "*.md"),
        ("All files", "*.*")
    ]
    filepath = filedialog.askopenfilename(title="Select File", filetypes=filetypes)
    if not filepath:
        return
    guessed_format = detect_format(filepath)
    if not guessed_format:
        messagebox.showerror("Error", "Unsupported file format.")
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        data = parse_content(content, guessed_format)
        framework_input.delete("1.0", tk.END)
        framework_input.insert(tk.END, content)
        format_var.set(guessed_format)
        logging.info(f"Uploaded and parsed file '{filepath}' successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        logging.error(f"File upload error: {e}")

def expand_framework_gui(openai_key: str, gemini_key: str):
    """
    Handles the framework expansion process from the GUI.
    """
    raw_text = framework_input.get("1.0", tk.END).strip()
    if not raw_text:
        messagebox.showerror("Error", "No framework content provided.")
        logging.warning("No framework content provided by the user.")
        return

    chosen_format = format_var.get()
    if not chosen_format:
        messagebox.showerror("Error", "Please select a format (YAML, JSON, Markdown).")
        logging.warning("No format selected by the user.")
        return

    model_choice = model_var.get()
    if not model_choice:
        messagebox.showerror("Error", "Please select a model.")
        logging.warning("No AI model selected by the user.")
        return

    try:
        data = parse_content(raw_text, chosen_format)
        logging.info(f"Parsed input content successfully in format '{chosen_format}'.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        logging.error(f"Parsing error: {e}")
        return

    # Start expansion in a separate thread
    logging.info(f"Initiating expansion using model '{model_choice}'.")
    threading.Thread(
        target=expand_framework_in_thread,
        args=(data, model_choice, chosen_format, gemini_key),
        daemon=True
    ).start()

###############################################################################
# 8) Export and Copy Functions
###############################################################################

def export_output():
    """
    Exports the expanded framework to a file in the selected format.
    """
    export_options = [
        ("YAML", "*.yaml"),
        ("JSON", "*.json"),
        ("Markdown", "*.md")
    ]
    file_path = filedialog.asksaveasfilename(
        title="Save Expanded Framework",
        defaultextension=".yaml",
        filetypes=export_options
    )
    if file_path:
        content = result_box.get("1.0", tk.END).strip()
        if not content:
            messagebox.showerror("Error", "No expanded output to save.")
            logging.warning("User attempted to export without any expanded output.")
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Success", f"Saved to {file_path}")
            logging.info(f"Exported expanded framework to '{file_path}'.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")
            logging.error(f"Failed to save file '{file_path}': {e}")

def copy_to_clipboard():
    """
    Copies the expanded framework output to the clipboard.
    """
    content = result_box.get("1.0", tk.END).strip()
    if not content:
        messagebox.showerror("Error", "Nothing to copy.")
        logging.warning("User attempted to copy without any expanded output.")
        return
    root.clipboard_clear()
    root.clipboard_append(content)
    messagebox.showinfo("Copied", "Output copied to clipboard!")
    logging.info("User copied the expanded framework to clipboard.")

###############################################################################
# 9) Main TKinter App
###############################################################################

def main():
    global root, framework_input, result_box
    global format_var, model_var

    # 1. Load API Keys
    OPENAI_API_KEY, GEMINI_API_KEY = load_api_keys()

    # 2. Create the GUI
    root = tk.Tk()
    root.title("AI-Assisted Framework Upscaler - Debug Mode")
    root.geometry("1200x800")

    logging.info("GUI created successfully.")

    # ========================
    #  FRAME: INPUT AREA
    # ========================
    input_frame = tk.Frame(root)
    input_frame.pack(padx=10, pady=10, fill=tk.BOTH)

    # Label for input
    lbl = tk.Label(input_frame, text="Paste or Upload Framework Content:")
    lbl.grid(row=0, column=0, sticky="w")

    # Text input widget
    framework_input = tk.Text(input_frame, wrap="word", width=100, height=20)
    framework_input.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

    # Format selection
    format_var = tk.StringVar()
    tk.Label(input_frame, text="Format:").grid(row=2, column=0, sticky="e")
    fmt_dropdown = tk.OptionMenu(input_frame, format_var, "YAML", "JSON", "Markdown")
    fmt_dropdown.config(width=12)
    fmt_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    # File upload button
    upload_btn = tk.Button(input_frame, text="Upload File", command=lambda: upload_file_gui(format_var))
    upload_btn.grid(row=2, column=2, padx=5, pady=5, sticky="e")

    # Clear input button
    clear_btn = tk.Button(input_frame, text="Clear", command=lambda: framework_input.delete("1.0", tk.END))
    clear_btn.grid(row=2, column=3, padx=5, pady=5, sticky="e")

    # ========================
    #  FRAME: MODEL SELECTION
    # ========================
    model_frame = tk.Frame(root)
    model_frame.pack(padx=10, pady=5, fill=tk.X)

    tk.Label(model_frame, text="Choose Model:").pack(side=tk.LEFT)

    model_var = tk.StringVar()
    model_dropdown = tk.OptionMenu(model_frame, model_var, "OpenAI GPT-4", "Gemini 1.5 Flash")
    model_dropdown.config(width=20)
    model_dropdown.pack(side=tk.LEFT, padx=5)

    # Expand button
    expand_btn = tk.Button(model_frame, text="Expand Framework", command=lambda: expand_framework_gui(OPENAI_API_KEY, GEMINI_API_KEY))
    expand_btn.pack(side=tk.LEFT, padx=10)

    # ========================
    #  FRAME: OUTPUT AREA
    # ========================
    output_frame = tk.Frame(root)
    output_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    tk.Label(output_frame, text="Expanded Output:").pack(anchor="w")
    result_box = tk.Text(output_frame, wrap="word", state=tk.DISABLED)
    result_box.pack(fill=tk.BOTH, expand=True)

    # ========================
    #  FRAME: EXPORT/COPY BUTTONS
    # ========================
    export_frame = tk.Frame(root)
    export_frame.pack(padx=10, pady=10, fill=tk.X)

    export_btn = tk.Button(export_frame, text="Export", command=export_output)
    export_btn.pack(side=tk.LEFT, padx=5)

    copy_btn = tk.Button(export_frame, text="Copy to Clipboard", command=copy_to_clipboard)
    copy_btn.pack(side=tk.LEFT, padx=5)

    logging.info("Starting the main event loop.")

    # Start the main event loop
    root.mainloop()

###############################################################################
# 10) Run the Application
###############################################################################

if __name__ == "__main__":
    main()
