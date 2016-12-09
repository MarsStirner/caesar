# coding: utf-8
from jinja2 import nodes, Markup
from jinja2.ext import Extension


class IncludeRbTemplateExtension(Extension):
    """
    Adds `include_rb_template` tag that loads template from database by
    (rbPrintTemplate.context, rbPrintTemplate.code) and
    renders it within the template.
    """
    # a set of names that trigger the extension.
    tags = set(['include_rb_template'])

    def __init__(self, environment):
        super(IncludeRbTemplateExtension, self).__init__(environment)

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        args = [parser.parse_expression()]  # context
        parser.stream.skip_if('comma')
        args.append(parser.parse_expression())  # code
        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())  # inner template context extender
        else:
            args.append(nodes.Const({}))

        ctx_ref = nodes.ContextReference()
        args.append(ctx_ref)
        node = self.call_method('_load_rb_template', args, lineno=lineno)

        return nodes.CallBlock(node, [], [], [], lineno=lineno)

    def _load_rb_template(self, context_code, template_code, context_extend, context_data, caller):
        # parent template runtime context
        ctx_data = context_data.parent
        ctx_data.update(context_extend)
        try:
            template_string = self.environment.applyInnerTemplate(
                context_code, template_code, ctx_data
            )
        except Exception, e:
            print 'Error render inner template (context={0}, code={1})'.format(context_code, template_code)
            raise e
        return Markup(template_string)
