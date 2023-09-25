def read_file(path: str) -> tuple[str, str]:
    try:
        f = open(file=path, mode='r')
        return f.read(), None
    except Exception as ex:
        return None, str(ex)

def write_file(content: str, path: str) -> str:
    try:
        f = open(file=path, mode='w')
        f.write(content)
        return None
    except Exception as ex:
        return str(ex)