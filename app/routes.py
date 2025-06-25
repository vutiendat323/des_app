import logging
from datetime import datetime
from typing import Dict
import random
from flask import Blueprint, render_template, request, send_file, session, url_for, redirect, flash,current_app
from flask_socketio import emit, join_room, leave_room
from flask_login import login_user, logout_user, login_required, current_user

from .models import User,Message
from . import db, bcrypt, socketio
from .forms import RegisterForm, LoginForm, EncryptionForm, DecryptionForm, FileEncryptionForm, FileDecryptionForm
from config import Config
from .utils.des import DES as CustomDES
import binascii
import base64
import os
import json


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

routes = Blueprint('routes', __name__)

# In-memory storage for active users
active_users: Dict[str, dict] = {}

def generate_guest_username() -> str:
    """Generate a unique guest username with timestamp to avoid collisions"""
    timestamp = datetime.now().strftime('%H%M')
    return f'Guest{timestamp}{random.randint(1000,9999)}'

@routes.route('/chat')
@login_required
def index():
    # Không cần gán session['username'] nữa
    logger.info(f"New user session created: {current_user.username}")
    
    return render_template(
        'index.html',
        username=current_user.username,
        rooms=Config.CHAT_ROOMS
    )

@socketio.event
def connect():
    try:
        if not current_user.is_authenticated:
            return False
    
        active_users[request.sid] = {
            'username': current_user.username,
            'connected_at': datetime.now().isoformat()
        }
        
        emit('active_users', {
            'users': [user['username'] for user in active_users.values()]
        }, broadcast=True)
        
        logger.info(f"User connected: {current_user.username}")
    
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        return False

@socketio.event
def disconnect():
    try:
        if request.sid in active_users:
            username = active_users[request.sid]['username']
            del active_users[request.sid]
            
            emit('active_users', {
                'users': [user['username'] for user in active_users.values()]
            }, broadcast=True)
            
            logger.info(f"User disconnected: {username}")
    
    except Exception as e:
        logger.error(f"Disconnection error: {str(e)}")

@socketio.on('join')
def on_join(data: dict):
    try:
        username = current_user.username
        room = data['room']
        
        if room not in Config.CHAT_ROOMS:
            logger.warning(f"Invalid room join attempt: {room}")
            return
        
        join_room(room)
        active_users[request.sid]['room'] = room
        
        emit('status', {
            'msg': f'{username} has joined the room.',
            'type': 'join',
            'timestamp': datetime.now().isoformat()
        }, room=room)
        
        logger.info(f"User {username} joined room: {room}")
    
    except Exception as e:
        logger.error(f"Join room error: {str(e)}")

@socketio.on('leave')
def on_leave(data: dict):
    try:
        username = current_user.username
        room = data['room']
        
        leave_room(room)
        if request.sid in active_users:
            active_users[request.sid].pop('room', None)
        
        emit('status', {
            'msg': f'{username} has left the room.',
            'type': 'leave',
            'timestamp': datetime.now().isoformat()
        }, room=room)
        
        logger.info(f"User {username} left room: {room}")
    
    except Exception as e:
        logger.error(f"Leave room error: {str(e)}")

@socketio.on('message')
def handle_message(data: dict):
    try:
        username = current_user.username
        room = data.get('room', 'General')
        msg_type = data.get('type', 'message')
        message = data.get('msg', '').strip()
        
        if not message:
            return
        
        timestamp = datetime.now().isoformat()
        
        if msg_type == 'private':
            target_user = data.get('target')
            if not target_user:
                return
            msg_obj = Message(
                username=username,
                room=room,
                content=message,
                type='private',
                target=target_user
            )
        else:
            if room not in Config.CHAT_ROOMS:
                logger.warning(f"Message to invalid room: {room}")
                return
            msg_obj = Message(
                username=username,
                room=room,
                content=message,
                type='message'
            )
        db.session.add(msg_obj)
        db.session.commit()

        if msg_type == 'private':
            # Handle private messages
            target_user = data.get('target')
            if not target_user:
                return
                
            for sid, user_data in active_users.items():
                if user_data['username'] == target_user:
                    emit('private_message', {
                        'msg': message,
                        'from': username,
                        'to': target_user,
                        'timestamp': timestamp
                    }, room=sid)
                    logger.info(f"Private message sent: {username} -> {target_user}")
                    return
                    
            logger.warning(f"Private message failed - user not found: {target_user}")
        
        else:
            # Regular room message
            if room not in Config.CHAT_ROOMS:
                logger.warning(f"Message to invalid room: {room}")
                return
                
            emit('message', {
                'msg': message,
                'username': username,
                'room': room,
                'timestamp': timestamp
            }, room=room)
            
            logger.info(f"Message sent in {room} by {username}")
    
    except Exception as e:
        logger.error(f"Message handling error: {str(e)}")


@socketio.on('get_history')
def get_history(data):
    room = data.get('room', 'General')
    messages = Message.query.filter_by(room=room, type='message').order_by(Message.timestamp.asc()).all()
    history = [{
        'username': m.username,
        'msg': m.content,
        'timestamp': m.timestamp.isoformat(),
        'type': m.type
    } for m in messages]
    emit('history', {'messages': history})

@socketio.on('get_history_private')
def get_history_private(data):
    target = data.get('target')
    username = current_user.username
    # Lấy tin nhắn private giữa 2 người (cả chiều đi và về)
    messages = Message.query.filter(
        Message.type == 'private',
        ((Message.username == username) & (Message.target == target)) |
        ((Message.username == target) & (Message.target == username))
    ).order_by(Message.timestamp.asc()).all()
    history = [{
        'username': m.username,
        'msg': m.content,
        'timestamp': m.timestamp.isoformat(),
        'type': m.type
    } for m in messages]
    emit('history_private', {'messages': history})

# Authentication
@routes.route('/')
def home():
    return render_template('home.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('routes.dashboard'))
    return render_template('login.html', form=form)


@routes.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@routes.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))


@ routes.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('routes.login'))

    return render_template('register.html', form=form)

# Encryption/Decryption
@routes.route('/encrypt', methods=['GET', 'POST'])
def encrypt():
    form = EncryptionForm()
    if form.validate_on_submit():
        plaintext = form.plaintext.data.encode('utf-8')
        key = form.key.data.encode('utf-8')
        mode = form.mode.data
        iv = form.iv.data.encode('utf-8') if mode in ['CBC', 'OFB', 'CFB'] else None
        output_format = form.output_format.data
        verbose = form.verbose.data

        if len(key) != 8:
            flash('Key must be 8 bytes!', 'error')
            return render_template('encrypt.html', form=form)
        if mode in ['CBC', 'OFB', 'CFB'] and (iv is None or len(iv) != 8):
            flash('IV must be 8 bytes for CBC, OFB, CFB modes!', 'error')
            return render_template('encrypt.html', form=form)

        try:
            des = CustomDES(key, mode=mode, iv=iv)
            ciphertext = des.encrypt(plaintext)
            
            if output_format == 'base64':
                encrypted_text = base64.b64encode(ciphertext).decode('utf-8')
            else:
                encrypted_text = binascii.hexlify(ciphertext).decode('utf-8')

            download_link = None
            if verbose:
                all_steps = des.get_steps()

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"encrypt_log_{timestamp}.json"

                log_dir = os.path.join("app", "static", "log")
                os.makedirs(log_dir, exist_ok=True)
                log_path = os.path.join(log_dir, filename)

                with open(log_path, "w", encoding="utf-8") as f:
                    json.dump(all_steps, f, indent=4)
                
                # Redirect to result page instead of showing download link
                return redirect(url_for('routes.result', filename=filename))
                
            return render_template('encrypt.html', encrypted_text=encrypted_text, download_link=download_link, form=form)
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('encrypt.html', encrypted_text=None,form=form)
    return render_template('encrypt.html', form=form)    

@routes.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    form = DecryptionForm()
    if form.validate_on_submit():
        ciphertext_input = form.ciphertext.data
        key = form.key.data.encode('utf-8')
        mode = form.mode.data
        iv = form.iv.data.encode('utf-8') if mode in ['CBC', 'OFB', 'CFB'] else None
        input_format = form.input_format.data
        verbose = form.verbose.data

        try:
            if input_format == 'base64':
                ciphertext = base64.b64decode(ciphertext_input)
            else:
                ciphertext = binascii.unhexlify(ciphertext_input)
        except (binascii.Error, ValueError):
            flash('Invalid input format!', 'error')
            return render_template('decrypt.html', decrypted_text=None, form=form)

        if len(key) != 8:
            flash('Key must be 8 bytes!', 'error')
            return render_template('decrypt.html', decrypted_text=None, form=form)
        if mode in ['CBC', 'OFB', 'CFB'] and (iv is None or len(iv) != 8):
            flash('IV must be 8 bytes for CBC, OFB, CFB modes!', 'error')
            return render_template('decrypt.html', decrypted_text=None, form=form)

        try:
            des = CustomDES(key, mode=mode, iv=iv)
            plaintext = des.decrypt(ciphertext)
            decrypted_text = plaintext.decode('utf-8', errors='ignore')

            download_link = None
            if verbose:
                all_steps = des.get_steps()

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"decrypt_log_{timestamp}.json"

                log_dir = os.path.join("app", "static", "log")
                os.makedirs(log_dir, exist_ok=True)
                log_path = os.path.join(log_dir, filename)

                with open(log_path, "w", encoding="utf-8") as f:
                    json.dump(all_steps, f, indent=4)
                
                # Redirect to result page instead of showing download link
                return redirect(url_for('routes.result', filename=filename))

            return render_template('decrypt.html', decrypted_text=decrypted_text, download_link=download_link, form=form)
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('decrypt.html', decrypted_text=None, form=form)

    return render_template('decrypt.html', form=form)

@routes.route('/result/<filename>')
def result(filename):
    log_path = os.path.join(current_app.root_path, 'static', 'log', filename)
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            steps_data = json.load(f)
        return render_template('result.html', steps=steps_data, filename=filename)
    except FileNotFoundError:
        flash('Result file not found!', 'error')
        return redirect(url_for('routes.encrypt'))
    except json.JSONDecodeError:
        flash('Error reading result file!', 'error')
        return redirect(url_for('routes.encrypt'))

@routes.route('/download/<filename>')
def download(filename):
    # log_path = os.path.join('app', 'static', 'log', filename)
    # abs_log_path = os.path.abspath(log_path)
    log_path = os.path.join(current_app.root_path, 'static', 'log', filename)
    return send_file( log_path,
                     as_attachment=True,
                     download_name=filename,
                     mimetype='text/plain')   

@routes.route('/download_file/<filename>')
def download_file(filename):
    file_path = os.path.join(current_app.root_path, 'static', 'uploads', filename)
    return send_file(file_path, as_attachment=True)

# File Encryption/Decryption using pycryptodome
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad

@routes.route('/des/file', methods=['GET', 'POST'])
def file_encrypt():
    form = FileEncryptionForm()
    if form.validate_on_submit():
        try:
            # Get file data
            file = form.file.data
            file_data = file.read()
            original_filename = file.filename
            
            # Get encryption parameters
            key = form.key.data.encode('utf-8')
            mode = form.mode.data
            iv = form.iv.data.encode('utf-8') if mode in ['CBC', 'OFB', 'CFB'] else None

            # Validate key and IV
            if len(key) != 8:
                flash('Key must be 8 bytes!', 'error')
                return render_template('file_encrypt.html', form=form)
            if mode in ['CBC', 'OFB', 'CFB'] and (iv is None or len(iv) != 8):
                flash('IV must be 8 bytes for CBC, OFB, CFB modes!', 'error')
                return render_template('file_encrypt.html', form=form)

            # Create DES cipher based on mode
            if mode == 'ECB':
                cipher = DES.new(key, DES.MODE_ECB)
            elif mode == 'CBC':
                cipher = DES.new(key, DES.MODE_CBC, iv)
            elif mode == 'OFB':
                cipher = DES.new(key, DES.MODE_OFB, iv)
            elif mode == 'CFB':
                cipher = DES.new(key, DES.MODE_CFB, iv)
            
            # Encrypt the file data with padding
            ciphertext = cipher.encrypt(pad(file_data, DES.block_size))
            
            # Create encrypted file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename, _ = os.path.splitext(original_filename)
            encrypted_filename = f"{base_filename}_{timestamp}.enc"
            
            # Save encrypted file
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            encrypted_file_path = os.path.join(upload_dir, encrypted_filename)
            
            with open(encrypted_file_path, 'wb') as f:
                f.write(ciphertext)
            
            # Create download link
            download_link = f'download_file/{encrypted_filename}'
            
            return render_template('file_encrypt.html', 
                                 form=form, 
                                 download_link=download_link,
                                 encrypted_filename=encrypted_filename)
                                 
        except Exception as e:
            flash(f'Encryption error: {str(e)}', 'error')
            return render_template('file_encrypt.html', form=form)
    
    return render_template('file_encrypt.html', form=form)

@routes.route('/des/file/decrypt', methods=['GET', 'POST'])
def file_decrypt():
    form = FileDecryptionForm()
    if form.validate_on_submit():
        try:
            # Get file data
            file = form.file.data
            file_data = file.read()
            original_filename = file.filename
            
            # Get decryption parameters
            key = form.key.data.encode('utf-8')
            mode = form.mode.data
            iv = form.iv.data.encode('utf-8') if mode in ['CBC', 'OFB', 'CFB'] else None

            # Validate key and IV
            if len(key) != 8:
                flash('Key must be 8 bytes!', 'error')
                return render_template('file_decrypt.html', form=form)
            if mode in ['CBC', 'OFB', 'CFB'] and (iv is None or len(iv) != 8):
                flash('IV must be 8 bytes for CBC, OFB, CFB modes!', 'error')
                return render_template('file_decrypt.html', form=form)

            # Create DES cipher based on mode
            if mode == 'ECB':
                cipher = DES.new(key, DES.MODE_ECB)
            elif mode == 'CBC':
                cipher = DES.new(key, DES.MODE_CBC, iv)
            elif mode == 'OFB':
                cipher = DES.new(key, DES.MODE_OFB, iv)
            elif mode == 'CFB':
                cipher = DES.new(key, DES.MODE_CFB, iv)
            
            # Decrypt the file data and remove padding
            plaintext = unpad(cipher.decrypt(file_data), DES.block_size)
            
            # Create decrypted file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            decrypted_filename = f"decrypted_{timestamp}.bin"
            
            # Save decrypted file
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            decrypted_file_path = os.path.join(upload_dir, decrypted_filename)
            
            with open(decrypted_file_path, 'wb') as f:
                f.write(plaintext)
            
            # Create download link
            download_link = f'download_file/{decrypted_filename}'
            
            return render_template('file_decrypt.html', 
                                 form=form, 
                                 download_link=download_link,
                                 decrypted_filename=decrypted_filename)
                                 
        except Exception as e:
            flash(f'Decryption error: {str(e)}', 'error')
            return render_template('file_decrypt.html', form=form)
    
    return render_template('file_decrypt.html', form=form) 
