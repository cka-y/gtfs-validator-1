import os
import glob
import requests

os_name = os.getenv("OS_NAME").split("-")[0]
github_token = os.getenv("GITHUB_TOKEN")
release_id = os.getenv("RELEASE_ID")
owner = os.getenv("OWNER")
repo = os.getenv("REPO")

headers = {
    "Authorization": f"token {github_token}",
    "Accept": "application/vnd.github.v3+json",
}

for file in glob.glob("./app/pkg/build/jpackage/*"):
    extension = file.split('.')[-1]
    if extension not in ["msi", "dmg", "pkg", "deb"]:
        continue

    print(f'Uploading {file}')

    with open(file, 'rb') as f:
        response = requests.post(
            f"https://uploads.github.com/repos/{owner}/{repo}/releases/{release_id}/assets?name=Installer%20{os_name}.{extension}",
            headers=headers,
            data=f.read()
        )

    response.raise_for_status()