def read_file(path: str) -> tuple[str, str]:
    with open(file=path, mode='r') as f:
        try:
            return f.read(), None
        except Exception as ex:
            return None, str(ex)

def write_file(content: str, path: str) -> str:
    with open(file=path, mode='w') as f:
        try:
            f.write(content)
            return None
        except Exception as ex:
            return str(ex)