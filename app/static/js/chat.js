let socket = io();
let currentRoom = 'General';
let username = document.getElementById('username').textContent;
let roomMessages = {};
let privateMessages = {};
let privateTarget = null;

// Socket event listeners
socket.on('connect', () => {
	joinRoom('General');
	highlightActiveRoom('General');
});

socket.on('message', (data) => {
	if (!privateTarget) {
		addMessage(
			data.username,
			data.msg,
			data.username === username ? 'own' : 'other'
		);
		if (!roomMessages[currentRoom]) roomMessages[currentRoom] = [];
		roomMessages[currentRoom].push({ sender: data.username, message: data.msg, type: data.username === username ? 'own' : 'other' });
	}
});

socket.on('private_message', (data) => {
	if (privateTarget === data.from) {
		addMessage(data.from, data.msg, 'other');
		if (!privateMessages[privateTarget]) privateMessages[privateTarget] = [];
		privateMessages[privateTarget].push({ sender: data.from, message: data.msg, type: 'other' });
	} else {
		showToast(`Bạn có tin nhắn mới từ ${data.from}`);
	}
});

socket.on('status', (data) => {
	if (!privateTarget) {
		addMessage('System', data.msg, 'system');
	}
});

socket.on('active_users', (data) => {
	const userList = document.getElementById('active-users');
	userList.innerHTML = data.users
		.map(
			(user) => `
            <div class="user-item" onclick="insertPrivateMessage('${user}')">
                ${user} ${user === username ? '(you)' : ''}
            </div>
        `
		)
		.join('');
});

// Message handling
function addMessage(sender, message, type) {
	const chat = document.getElementById('chat');
	const messageDiv = document.createElement('div');

	if (privateTarget) {
		if (sender === username) {
			messageDiv.className = 'message own';
			messageDiv.textContent = message;
		} else {
			messageDiv.className = 'message other';
			messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
		}
	} else {
		messageDiv.className = `message ${type}`;
		if (type === 'system') {
			messageDiv.textContent = message;
		} else if (type === 'private') {
			if (sender === username) {
				messageDiv.textContent = message;
			} else {
				messageDiv.innerHTML = `<strong>${sender} (private):</strong> ${message}`;
			}
		} else if (type === 'own') {
			messageDiv.textContent = message;
		} else {
			messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
		}
	}

	chat.appendChild(messageDiv);
	chat.scrollTop = chat.scrollHeight;
}

function sendMessage() {
	const input = document.getElementById('message');
	const message = input.value.trim();

	if (!message) return;

	if (privateTarget) {
		// Gửi tin nhắn riêng
		socket.emit('message', {
			msg: message,
			type: 'private',
			target: privateTarget,
		});
		// Lưu và hiển thị luôn tin nhắn mình vừa gửi
		if (!privateMessages[privateTarget]) privateMessages[privateTarget] = [];
		privateMessages[privateTarget].push({ sender: username, message, type: 'own' });
		addMessage(username, message, 'own');
	} else {
		// Gửi room message
		socket.emit('message', {
			msg: message,
			room: currentRoom,
		});
	}

	input.value = '';
	input.focus();
}

function joinRoom(room) {
	privateTarget = null;
	socket.emit('leave', { room: currentRoom });
	currentRoom = room;
	socket.emit('join', { room });
	socket.emit('get_history', { room: room });
	highlightActiveRoom(room);
	document.querySelector('.main-chat-header').textContent = `Room: ${room}`;
	const chat = document.getElementById('chat');
	chat.innerHTML = '';
	// Nếu đã có lịch sử, render lại
	if (roomMessages[room]) {
		roomMessages[room].forEach(msg => {
			addMessage(msg.sender, msg.message, msg.type);
		});
	}
}

function insertPrivateMessage(user) {
	privateTarget = user;
	socket.emit('get_history_private', { target: user });
	document.querySelector('.main-chat-header').textContent = `Chat with ${user}`;
	const chat = document.getElementById('chat');
	chat.innerHTML = '';
	if (privateMessages[user]) {
		privateMessages[user].forEach(msg => {
			addMessage(msg.sender, msg.message, msg.type);
		});
	}
}

function handleKeyPress(event) {
	if (event.key === 'Enter' && !event.shiftKey) {
		event.preventDefault();
		sendMessage();
	}
}

// Initialize chat when page loads
let chat;
document.addEventListener('DOMContentLoaded', () => {
	chat = new ChatApp();
	if ('Notification' in window) {
		Notification.requestPermission();
	}
});

// Add this new function to handle room highlighting
function highlightActiveRoom(room) {
	document.querySelectorAll('.room-item').forEach((item) => {
		item.classList.remove('active-room');
		if (item.textContent.trim() === room) {
			item.classList.add('active-room');
		}
	});
}

socket.on('history', (data) => {
	const chat = document.getElementById('chat');
	chat.innerHTML = '';
	roomMessages[currentRoom] = [];

	data.messages.forEach((msg) => {
		roomMessages[currentRoom].push({
			sender: msg.username,
			message: msg.msg,
			type: msg.type === 'private' ? 'private' : (msg.username === username ? 'own' : 'other')
		});
		addMessage(
			msg.username,
			msg.msg,
			msg.type === 'private' ? 'private' : (msg.username === username ? 'own' : 'other')
		);
	});
});

// Lắng nghe lịch sử chat riêng
socket.on('history_private', (data) => {
	const chat = document.getElementById('chat');
	chat.innerHTML = '';
	privateMessages[privateTarget] = [];
	data.messages.forEach((msg) => {
		privateMessages[privateTarget].push({
			sender: msg.username,
			message: msg.msg,
			type: msg.username === username ? 'own' : 'other'
		});
		addMessage(
			msg.username,
			msg.msg,
			msg.username === username ? 'own' : 'other'
		);
	});
});

function showToast(msg) {
	let toast = document.createElement('div');
	toast.className = 'toast-notify';
	toast.textContent = msg;
	document.body.appendChild(toast);
	setTimeout(() => { toast.remove(); }, 4000);
}