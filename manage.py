#!/usr/bin/env python
import os
import sys
from django.conf import settings


def main():
    # Set the default settings module if not already set
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastener_manager.settings')
    print("real DJANGO_SETTINGS_MODULE")
    print(os.environ.get("DJANGO_SETTINGS_MODULE"))

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # This error occurs if Django is not installed or cannot be found
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Execute the command-line utility
    print("sys.argv: ")
    print(sys.argv)
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
