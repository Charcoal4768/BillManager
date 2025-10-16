from jinja2 import pass_context

@pass_context
def slugify(context, value):
    return value.lower().replace(" ", "-")

#split filter
@pass_context
def split(context, value, delimiter=","):
    return value.split(delimiter)