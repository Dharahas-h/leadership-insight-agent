import { API_BASE_URL } from '../constants';

class SocketManager {
  socket = null;
  connect(onMessage) {
    const sessionId = crypto.randomUUID();
    this.socket = new WebSocket(`${API_BASE_URL}/chat?sessionId=${sessionId}`);
    this.socket.onopen = event => {
      console.log('Web socket connection open');
    };

    this.socket.onmessage = onMessage;
  }

  sendMessage(payload) {
    if (this.socket) {
      this.socket.send(JSON.stringify(payload));
    } else {
      throw new Error("Connection isn't initialised yet..");
    }
  }

  close() {
    if (this.socket) {
      this.socket.close();
      console.log('Web socket connection closed');
    } else {
      console.log('Web socket connection already closed');
    }
  }
}

export const socketManager = new SocketManager();
