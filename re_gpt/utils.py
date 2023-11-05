import hashlib
import os
import platform

current_os = platform.system()
current_file_directory = "/".join(
    __file__.split("\\" if current_os == "Windows" else "/")[0:-1]
)

funcaptcha_bin_folder_path = f"{current_file_directory}/funcaptcha_bin"
latest_release_url = (
    "https://api.github.com/repos/Zai-Kun/reverse-engineered-chatgpt/releases/latest"
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


async def download_binary(session, output_path, file_url):
    with open(output_path, "wb") as output_file:
        response = await session.get(
            url=file_url, content_callback=lambda chunk: output_file.write(chunk)
        )


async def get_binary_path(session):
    if binary_path is None:
        return None

    if not os.path.exists(funcaptcha_bin_folder_path) or not os.path.isdir(
        funcaptcha_bin_folder_path
    ):
        os.mkdir(funcaptcha_bin_folder_path)

    if os.path.isfile(binary_path):
        local_binary_hash = calculate_file_md5(binary_path)
        response = await session.get(latest_release_url)
        json_data = response.json()

        for line in json_data["body"].splitlines():
            if line.startswith(current_os):
                latest_binary_hash = line.split("=")[-1]
                break

        if local_binary_hash != latest_binary_hash:
            file_url = [
                asset
                for asset in json_data["assets"]
                if asset["name"] == binary_file_name
            ][0]["browser_download_url"]

            await download_binary(session, binary_path, file_url)
    else:
        response = await session.get(latest_release_url)
        json_data = response.json()

        file_url = [
            asset for asset in json_data["assets"] if asset["name"] == binary_file_name
        ][0]["browser_download_url"]

        await download_binary(session, binary_path, file_url)

    return binary_path
