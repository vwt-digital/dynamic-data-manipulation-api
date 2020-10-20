#!/usr/bin/env python3

from . import get_app


def main():
    app = get_app()
    app.run(port=8080)


if __name__ == '__main__':
    main()
