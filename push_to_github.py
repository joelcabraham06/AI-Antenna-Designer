import os
import base64
import httpx
import sys

GITHUB_USERNAME = "joelcabraham06"
REPO_NAME = "AI-Antenna-Designer"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()

IGNORE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}
IGNORE_FILES = {".DS_Store"}

def is_ignored(path):
    rel_path = os.path.relpath(path, PROJECT_DIR)
    parts = rel_path.split(os.sep)
    for part in parts:
        if part in IGNORE_DIRS or part in IGNORE_FILES:
            return True
    return False

def get_all_files():
    files_to_upload = []
    for root, dirs, files in os.walk(PROJECT_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            full_path = os.path.join(root, f)
            if not is_ignored(full_path):
                rel_path = os.path.relpath(full_path, PROJECT_DIR).replace("\\", "/")
                files_to_upload.append((full_path, rel_path))
    return files_to_upload

def upload_to_github(pat_token):
    headers = {
        "Authorization": f"Bearer {pat_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    files = get_all_files()
    print(f"Found {len(files)} files to upload to https://github.com/{GITHUB_USERNAME}/{REPO_NAME}...", flush=True)

    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        # Step 1: Ensure repository exists
        repo_res = client.get(f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}", headers=headers)
        if repo_res.status_code == 404:
            print(f"Creating repository {GITHUB_USERNAME}/{REPO_NAME}...", flush=True)
            create_payload = {
                "name": REPO_NAME,
                "description": "📡 AI-assisted automatic antenna synthesis & optimization using Python and ANSYS HFSS/AEDT, combining ML surrogate models, automated EM simulation, and multi-objective GA.",
                "private": False,
                "auto_init": True
            }
            create_res = client.post("https://api.github.com/user/repos", headers=headers, json=create_payload)
            if create_res.status_code in (200, 201):
                print(f"[OK] Created repository {GITHUB_USERNAME}/{REPO_NAME}!", flush=True)
            else:
                print(f"[FAIL] Error creating repo: {create_res.status_code} - {create_res.text}", flush=True)
                return False

        # Step 2: Upload Files
        success_count = 0
        fail_count = 0

        for full_path, rel_path in files:
            try:
                with open(full_path, "rb") as fp:
                    content_bytes = fp.read()
                content_b64 = base64.b64encode(content_bytes).decode("utf-8")
                
                url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{rel_path}"
                get_res = client.get(url, headers=headers)
                sha = None
                if get_res.status_code == 200:
                    sha = get_res.json().get("sha")
                    
                payload = {
                    "message": f"Add/Update {rel_path} via AI-Antenna-Designer Deployer",
                    "content": content_b64,
                    "branch": "main"
                }
                if sha:
                    payload["sha"] = sha
                    
                put_res = client.put(url, headers=headers, json=payload)
                if put_res.status_code in (200, 201):
                    print(f"[OK] Uploaded: {rel_path}", flush=True)
                    success_count += 1
                else:
                    print(f"[FAIL] Failed: {rel_path} ({put_res.status_code}: {put_res.text})", flush=True)
                    fail_count += 1
            except Exception as e:
                print(f"[FAIL] Error uploading {rel_path}: {e}", flush=True)
                fail_count += 1

        # Step 3: Update topics & metadata
        topics_payload = {
            "names": [
                "antenna-design", "ansys-hfss", "pyaedt", "electromagnetics", 
                "rf-engineering", "machine-learning", "genetic-algorithm", 
                "surrogate-model", "python"
            ]
        }
        client.put(f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/topics", headers=headers, json=topics_payload)

    print(f"\n==========================================", flush=True)
    print(f"Upload Complete! {success_count} succeeded, {fail_count} failed.", flush=True)
    print(f"Repository: https://github.com/{GITHUB_USERNAME}/{REPO_NAME}", flush=True)
    print(f"==========================================\n", flush=True)
    return fail_count == 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python push_to_github.py <PAT_TOKEN>")
        sys.exit(1)
    upload_to_github(sys.argv[1])
