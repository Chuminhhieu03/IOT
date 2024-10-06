from marshmallow import Schema, fields

class UserSchema(Schema):
    class Meta:
        fields = ('id', 'name', 'address', 'email')

class LogSchema(Schema):
    class Meta:
        fields = ('user_id', 'name', 'timeget')