import os
from multiprocessing import current_process

version = "3.7.2"

install_script = os.path.join(os.path.dirname(__file__), 'lib', 'install.sh')

try:
    import cv2  # noqa: F401
    import face_recognition  # noqa: F401
    import playsound  # noqa: F401
    import pvporcupine  # noqa: F401
    import pyaudio  # noqa: F401
    import pynotification  # noqa: F401
except ImportError as error:
    try:
        pynotification.pynotifier(title="First time user?", dialog=True, message=f"Please run\n\n{install_script}")
    except NameError:
        pass
    raise UserWarning(f"{error.__str__()}\n\nPlease run\n\n{install_script}\n\n"
                      "Note: Shell script will quit for any non-zero exit status, "
                      "so it might have to be triggered twice.")
else:
    if current_process().name == 'MainProcess':
        current_process().name = 'JARVIS'
    from ._preexec import keywords_handler  # noqa: F401
    from .main import start  # noqa: F401
