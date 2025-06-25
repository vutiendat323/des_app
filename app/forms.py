from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import BooleanField, SelectField, StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from .models import User

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

class EncryptionForm(FlaskForm):
    plaintext = StringField('Plaintext', validators=[
    ], render_kw={"placeholder": "Enter plaintext"})
    
    key = StringField('Key', validators=[
        InputRequired(message="Key is required"),
        Length(min=8, message="Key must be at least 8 characters long")
    ], render_kw={"placeholder": "Enter key"})

    mode = SelectField('Mode', choices=[('ECB', 'ECB'), ('CBC', 'CBC'), ('OFB', 'OFB'), ('CFB', 'CFB')], default='ECB', validators=[
        InputRequired(message="Mode is required")
    ])

    iv = StringField('IV', render_kw={"placeholder": "Enter IV (required for non-ECB modes)"})

    verbose = BooleanField('Verbose', default=False)

    output_format = SelectField('Output Format', choices=[('hex', 'Hex'), ('base64', 'Base64')], default='hex', validators=[
        InputRequired(message="Output format is required")
    ])

    submit = SubmitField('Encrypt')

    def validate_iv(self, iv):
        if self.mode.data != 'ECB':
            if not iv.data:
                raise ValidationError('IV is required for non-ECB modes.')
            if len(iv.data) != 8:
                raise ValidationError('IV must be exactly 8 characters long for non-ECB modes.')
        else:
            if iv.data:
                raise ValidationError('IV is not required for ECB mode.')

class DecryptionForm(FlaskForm):
    ciphertext = StringField('Ciphertext', validators=[
    ], render_kw={"placeholder": "Enter ciphertext"})
    
    key = StringField('Key', validators=[
        InputRequired(message="Key is required"),
        Length(min=8, message="Key must be at least 8 characters long")
    ], render_kw={"placeholder": "Enter key"})

    mode = SelectField('Mode', choices=[('ECB', 'ECB'), ('CBC', 'CBC'), ('OFB', 'OFB'), ('CFB', 'CFB')], default='ECB', validators=[
        InputRequired(message="Mode is required")
    ])

    iv = StringField('IV', render_kw={"placeholder": "Enter IV (required for non-ECB modes)"})

    verbose = BooleanField('Verbose', default=False)

    input_format = SelectField('Input Format', choices=[('hex', 'Hex'), ('base64', 'Base64')], default='hex', validators=[
        InputRequired(message="Input format is required")
    ])

    submit = SubmitField('Decrypt')

    def validate_iv(self, iv):
        if self.mode.data != 'ECB':
            if not iv.data:
                raise ValidationError('IV is required for non-ECB modes.')
            if len(iv.data) != 8:
                raise ValidationError('IV must be exactly 8 characters long for non-ECB modes.')
        else:
            if iv.data:
                raise ValidationError('IV is not required for ECB mode.')

class FileEncryptionForm(FlaskForm):
    file = FileField('File', validators=[
        FileRequired(message="Please select a file to encrypt"),
        FileAllowed(['txt', 'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif', 'zip', 'rar', 'mp3', 'mp4', 'avi', 'mov'], 
                   message="File type not allowed. Please upload a valid file.")
    ])
    
    key = StringField('Key', validators=[
        InputRequired(message="Key is required"),
        Length(min=8, message="Key must be at least 8 characters long")
    ], render_kw={"placeholder": "Enter key"})

    mode = SelectField('Mode', choices=[('ECB', 'ECB'), ('CBC', 'CBC'), ('OFB', 'OFB'), ('CFB', 'CFB')], default='ECB', validators=[
        InputRequired(message="Mode is required")
    ])

    iv = StringField('IV', render_kw={"placeholder": "Enter IV (required for non-ECB modes)"})

    submit = SubmitField('Encrypt File')

    def validate_iv(self, iv):
        if self.mode.data != 'ECB':
            if not iv.data:
                raise ValidationError('IV is required for non-ECB modes.')
            if len(iv.data) != 8:
                raise ValidationError('IV must be exactly 8 characters long for non-ECB modes.')
        else:
            if iv.data:
                raise ValidationError('IV is not required for ECB mode.')

class FileDecryptionForm(FlaskForm):
    file = FileField('Encrypted File', validators=[
        FileRequired(message="Please select an encrypted file to decrypt"),
        FileAllowed(['enc', 'bin', 'dat'], message="Please upload an encrypted file (.enc, .bin, .dat)")
    ])
    
    key = StringField('Key', validators=[
        InputRequired(message="Key is required"),
        Length(min=8, message="Key must be at least 8 characters long")
    ], render_kw={"placeholder": "Enter key"})

    mode = SelectField('Mode', choices=[('ECB', 'ECB'), ('CBC', 'CBC'), ('OFB', 'OFB'), ('CFB', 'CFB')], default='ECB', validators=[
        InputRequired(message="Mode is required")
    ])

    iv = StringField('IV', render_kw={"placeholder": "Enter IV (required for non-ECB modes)"})

    submit = SubmitField('Decrypt File')

    def validate_iv(self, iv):
        if self.mode.data != 'ECB':
            if not iv.data:
                raise ValidationError('IV is required for non-ECB modes.')
            if len(iv.data) != 8:
                raise ValidationError('IV must be exactly 8 characters long for non-ECB modes.')
        else:
            if iv.data:
                raise ValidationError('IV is not required for ECB mode.')

