from flask.ext.wtf import Form, TextField, Required 

class  CreateTemplateForm(Form):
    name = TextField('name', validators = [Required()], default=u"Template3")