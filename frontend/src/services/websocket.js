/**
 * WebSocket Client for Real-Time Updates
 * Handles connection, reconnection, message routing, and event dispatch
 */

class WebSocketManager {
  constructor(options = {}) {
    this.url = options.url || this.getWebSocketURL();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = options.maxReconnectAttempts || 5;
    this.reconnectDelay = options.reconnectDelay || 3000;
    this.listeners = new Map();
    this.messageQueue = [];
    this.isConnected = false;
    this.ws = null;
  }

  getWebSocketURL() {
    const backendUrl = window.ENV?.BACKEND_URL || 'http://localhost:8000';
    const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const baseUrl = backendUrl.replace(/^https?:\/\//, '');
    return `${wsProtocol}://${baseUrl}/ws`;
  }

  connect() {
    if (this.isConnected || this.ws) {
      console.log('WebSocket already connected');
      return;
    }

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => this.handleOpen();
      this.ws.onmessage = (event) => this.handleMessage(event);
      this.ws.onerror = (error) => this.handleError(error);
      this.ws.onclose = () => this.handleClose();
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.scheduleReconnect();
    }
  }

  handleOpen() {
    console.log('WebSocket connected');
    this.isConnected = true;
    this.reconnectAttempts = 0;

    // Emit connection event
    this.emit('connected', { timestamp: new Date() });

    // Process queued messages
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
  }

  handleMessage(event) {
    try {
      const message = JSON.parse(event.data);
      const { type, payload, timestamp } = message;

      // Emit specific event type
      if (type) {
        this.emit(type, {
          ...payload,
          timestamp: timestamp || new Date(),
          raw: message,
        });
      }

      // Emit generic message event
      this.emit('message', message);
    } catch (error) {
      console.error('WebSocket message parse error:', error);
    }
  }

  handleError(error) {
    console.error('WebSocket error:', error);
    this.emit('error', error);
  }

  handleClose() {
    console.log('WebSocket disconnected');
    this.isConnected = false;
    this.ws = null;

    this.emit('disconnected', { timestamp: new Date() });

    // Attempt reconnection
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.scheduleReconnect();
    } else {
      this.emit('reconnect_failed', {
        attempts: this.reconnectAttempts,
        maxAttempts: this.maxReconnectAttempts,
      });
    }
  }

  scheduleReconnect() {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * this.reconnectAttempts;

    console.log(
      `Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`
    );

    this.emit('reconnecting', {
      attempt: this.reconnectAttempts,
      delay,
    });

    setTimeout(() => {
      this.connect();
    }, delay);
  }

  send(message) {
    if (!this.isConnected) {
      console.warn('WebSocket not connected, queueing message:', message);
      this.messageQueue.push(message);
      return;
    }

    try {
      this.ws.send(JSON.stringify(message));
    } catch (error) {
      console.error('WebSocket send error:', error);
    }
  }

  subscribe(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType).push(callback);

    // Return unsubscribe function
    return () => {
      const callbacks = this.listeners.get(eventType);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    };
  }

  unsubscribe(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      return;
    }
    const callbacks = this.listeners.get(eventType);
    const index = callbacks.indexOf(callback);
    if (index > -1) {
      callbacks.splice(index, 1);
    }
  }

  emit(eventType, payload) {
    if (!this.listeners.has(eventType)) {
      return;
    }
    this.listeners.get(eventType).forEach((callback) => {
      try {
        callback(payload);
      } catch (error) {
        console.error(`Error in ${eventType} listener:`, error);
      }
    });
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
    }
  }

  getStatus() {
    return {
      connected: this.isConnected,
      url: this.url,
      reconnectAttempts: this.reconnectAttempts,
      maxReconnectAttempts: this.maxReconnectAttempts,
      queuedMessages: this.messageQueue.length,
    };
  }
}

// Export singleton instance
export const wsManager = new WebSocketManager();

export default WebSocketManager;
