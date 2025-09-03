from jinja2 import pass_context

@pass_context
def slugify(context, value):
    return value.lower().replace(" ", "-")