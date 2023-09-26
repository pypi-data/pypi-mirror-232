from jinja2 import Template

def generate_output(data: dict, content: str) -> tuple[str, str]:
    try:
        template = Template(content)
        output = template.render(data)
        return output, None
    except Exception as ex:
        return None, str(ex)