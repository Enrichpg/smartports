/**
 * WebSocket Client for Real-Time Updates
 * Handles connection, reconnection, message routing, and event dispatch
 */

class WebSocketManager {
  constructor(options = {}) {
    this.url = options.url || this.getWebSocketURL();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
    this.reconnectDelay = options.reconnectDelay || 3000;
    this.listeners = new Map();
    this.messageQueue = [];
    this.isConnected = false;
    this.ws = null;
    this._heartbeatInterval = null;
  }

  getWebSocketURL() {
    // Use explicit WS_URL from environment config (set in index.html)
    if (window.ENV?.WS_URL) return window.ENV.WS_URL;
    // Fallback: derive from current host
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    return `${proto}://${window.location.host}/api/v1/realtime/ws`;
  }

  connect() {
    if (this.isConnected || this.ws) {
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
    console.log('[WS] Connected to', this.url);
    this.isConnected = true;
    this.reconnectAttempts = 0;

    this.emit('connected', { timestamp: new Date() });

    // Flush queued messages
    while (this.messageQueue.length > 0) {
      this.send(this.messageQueue.shift());
    }

    // Keepalive ping every 25s
    this._heartbeatInterval = setInterval(() => {
      this.send({ type: 'ping' });
    }, 25000);
  }

  handleMessage(event) {
    try {
      const message = JSON.parse(event.data);
      const { type, data } = message;

      if (type === 'pong') {
        // Heartbeat acknowledged — nothing to do
        return;
      }

      if (type === 'event' && data?.event) {
        // Backend sends: { type: "event", data: { event: "berth.updated", payload: {...}, scope: {...}, entity: {...}, ... } }
        // Emit under the specific event name so pages can subscribe directly
        this.emit(data.event, {
          payload: data.payload || {},
          scope: data.scope || {},
          entity: data.entity || {},
          severity: data.severity,
          timestamp: data.timestamp || message.timestamp,
          raw: data,
        });
        // Also emit the generic 'event' for any catch-all listeners
        this.emit('event', data);
        return;
      }

      if (type === 'subscription_confirmed') {
        this.emit('subscription_confirmed', data);
        return;
      }

      // Generic fallback
      this.emit(type, data);
    } catch (error) {
      console.error('[WS] Message parse error:', error);
    }
  }

  handleError(error) {
    console.error('[WS] Error:', error);
    this.emit('error', error);
  }

  handleClose() {
    console.log('[WS] Disconnected');
    this.isConnected = false;
    this.ws = null;

    clearInterval(this._heartbeatInterval);
    this._heartbeatInterval = null;

    this.emit('disconnected', { timestamp: new Date() });

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
    // Exponential backoff capped at 30s
    const delay = Math.min(this.reconnectDelay * this.reconnectAttempts, 30000);

    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    this.emit('reconnecting', { attempt: this.reconnectAttempts, delay });

    setTimeout(() => this.connect(), delay);
  }

  send(message) {
    if (!this.isConnected) {
      this.messageQueue.push(message);
      return;
    }
    try {
      this.ws.send(JSON.stringify(message));
    } catch (error) {
      console.error('[WS] Send error:', error);
    }
  }

  subscribe(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType).push(callback);

    return () => {
      const callbacks = this.listeners.get(eventType);
      const index = callbacks.indexOf(callback);
      if (index > -1) callbacks.splice(index, 1);
    };
  }

  unsubscribe(eventType, callback) {
    const callbacks = this.listeners.get(eventType);
    if (!callbacks) return;
    const index = callbacks.indexOf(callback);
    if (index > -1) callbacks.splice(index, 1);
  }

  emit(eventType, payload) {
    const callbacks = this.listeners.get(eventType);
    if (!callbacks) return;
    callbacks.forEach((cb) => {
      try {
        cb(payload);
      } catch (error) {
        console.error(`[WS] Error in '${eventType}' listener:`, error);
      }
    });
  }

  disconnect() {
    clearInterval(this._heartbeatInterval);
    this._heartbeatInterval = null;
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

export const wsManager = new WebSocketManager();
export default WebSocketManager;
