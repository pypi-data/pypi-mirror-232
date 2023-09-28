import subprocess

def run(script_path):
    try:
        subprocess.run(["python", script_path], check=True)
        print(f"Script '{script_path}' executed successfully.")
    except subprocess.CalledProcessError:
        print(f"Error executing script '{script_path}'.")
