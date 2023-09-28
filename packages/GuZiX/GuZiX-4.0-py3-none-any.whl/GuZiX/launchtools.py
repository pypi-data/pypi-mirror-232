import subprocess

def run(apppath):
    try:
        # Use subprocess.run() to run the specified application
        subprocess.run(apppath, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
