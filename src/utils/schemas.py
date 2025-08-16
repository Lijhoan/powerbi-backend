from marshmallow import Schema, fields, validate

class LoginSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, validate=validate.Length(min=6))

class CommentSchema(Schema):
    contenido = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    report_id = fields.Int(required=True)

class ReactionSchema(Schema):
    tipo = fields.Str(required=True, validate=validate.OneOf(['me_interesa', 'increible', 'aporta']))
    report_id = fields.Int(required=True)

