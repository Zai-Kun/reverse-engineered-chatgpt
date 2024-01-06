import hashlib
import os
import platform

current_os = platform.system()
current_file_directory = "/".join(
    __file__.split("\\" if current_os == "Windows" else "/")[0:-1]
)

funcaptcha_bin_folder_path = f"{current_file_directory}/funcaptcha_bin"
latest_release_url = (
    "https://api.github.com/repos/Zai-Kun/reverse-engineered-chatgpt/releases"
)

binary_file_name = {"Windows": "windows_arkose.dll", "Linux": "linux_arkose.so"}.get(
    current_os
)

binary_path = {
    "Windows": f"{funcaptcha_bin_folder_path}/{binary_file_name}",
    "Linux": f"{funcaptcha_bin_folder_path}/{binary_file_name}",
}.get(current_os)


def calculate_file_md5(file_path):
    with open(file_path, "rb") as file:
        file_content = file.read()
        md5_hash = hashlib.md5(file_content).hexdigest()
        return md5_hash


def get_file_url(json_data):
    for release in json_data:
        if release["tag_name"].startswith("funcaptcha_bin"):
            file_url = next(
                asset["browser_download_url"]
                for asset in release["assets"]
                if asset["name"] == binary_file_name
            )
            return file_url


# async
async def async_download_binary(session, output_path, file_url):
    with open(output_path, "wb") as output_file:
        response = await session.get(
            url=file_url, content_callback=lambda chunk: output_file.write(chunk)
        )


async def async_get_binary_path(session):
    if binary_path is None:
        return None

    if not os.path.exists(funcaptcha_bin_folder_path) or not os.path.isdir(
        funcaptcha_bin_folder_path
    ):
        os.mkdir(funcaptcha_bin_folder_path)

    if os.path.isfile(binary_path):
        try:
            local_binary_hash = calculate_file_md5(binary_path)
            response = await session.get(latest_release_url)
            json_data = response.json()

            for line in json_data["body"].splitlines():
                if line.startswith(current_os):
                    latest_binary_hash = line.split("=")[-1]
                    break

            if local_binary_hash != latest_binary_hash:
                file_url = get_file_url(json_data)

                await async_download_binary(session, binary_path, file_url)
        except:
            return binary_path
    else:
        response = await session.get(latest_release_url)
        json_data = response.json()
        file_url = get_file_url(json_data)

        await async_download_binary(session, binary_path, file_url)

    return binary_path


# sync
def sync_download_binary(session, output_path, file_url):
    with open(output_path, "wb") as output_file:
        response = session.get(
            url=file_url, content_callback=lambda chunk: output_file.write(chunk)
        )


def sync_get_binary_path(session):
    if binary_path is None:
        return None

    if not os.path.exists(funcaptcha_bin_folder_path) or not os.path.isdir(
        funcaptcha_bin_folder_path
    ):
        os.mkdir(funcaptcha_bin_folder_path)

    if os.path.isfile(binary_path):
        try:
            local_binary_hash = calculate_file_md5(binary_path)
            response = session.get(latest_release_url)
            json_data = response.json()

            for line in json_data["body"].splitlines():
                if line.startswith(current_os):
                    latest_binary_hash = line.split("=")[-1]
                    break

            if local_binary_hash != latest_binary_hash:
                file_url = get_file_url(json_data)

                sync_download_binary(session, binary_path, file_url)
        except:
            return binary_path
    else:
        response = session.get(latest_release_url)
        json_data = response.json()
        file_url = get_file_url(json_data)

        sync_download_binary(session, binary_path, file_url)

    return binary_path


def get_model_slug(chat):
    for _, message in chat.get("mapping", {}).items():
        if "message" in message:
            role = message["message"]["author"]["role"]
            if role == "assistant":
                return message["message"]["metadata"]["model_slug"]
