from lia.conversation.emojis import angered_face, sailboat
from click import echo


def say_podman_missing() -> None:
    message = base_message("podman", "podman")
    echo(message)


def say_lxc_missing() -> None:
    message = base_message("lxc", "lxc")
    echo(message)


def base_message(missing_container_software: str, package_name: str) -> str:
    message = (
        f"{angered_face} You don't have {missing_container_software} installed {angered_face}."
        f"Please install podman now. In case your forgot how, I prepared you the command{sailboat}\n"
        f"sudo apt install {package_name}"
    )
