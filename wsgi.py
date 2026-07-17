import os
import sys

APP_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "skillcheck and que system (AI)", "skillcheck_ai arman", "skillcheck_ai", "skillcheck_ai",
)
sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)

from app import app  # noqa: E402  (the real Flask app, one dir down)
