/**
 * WebSocket Client for Real-Time Updates
 * Handles connection, reconnection, message routing, and event dispatch
 * 
 * Features:
 * - Auto-reconnection with exponential backoff
 * - Heartbeat/ping-pong for connection health
 * - Event-based message routing
 * - Message queue for offline scenarios
 * - Comprehensive error handling and logging
 */

class WebSocketManager {
  constructor(options = {}) {
    this.url = options.url || this.getWebSocketURL();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
    this.reconnectDelay = options.reconnectDelay || 2000;
    this.maxReconnectDelay = options.maxReconnectDelay || 30000;
    this.heartbeatInterval = options.heartbeatInterval || 30000; // 30 seconds
    
    this.listeners = new Map();
    this.messageQueue = [];
    this.isConnected = false;
    this.ws = null;
    this.heartbeatTimer = null;
    
    if (window.ENV?.DEBUG) {
      console.log('[WebSocket] Initialized with URL:', this.url);
    }
  }

  getWebSocketURL() {
    // Use environment configuration if available
    if (window.ENV?.WS_URL) {
      return window.ENV.WS_URL;
    }
    
    // Fallback: construct from BACKEND_URL
    const backendUrl = window.ENV?.BACKEND_URL || 'http://localhost:8000/api/v1';
    const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const baseUrl = backendUrl.replace(/^https?:\/\//, '').replace(/\/api\/v1$/, '');
    return `${wsProtocol}://${baseUrl}/api/v1/realtime/ws`;
  }

  connect() {
    if (this.isConnected || this.ws) {
      console.log('[WebSocket] Already connected or connecting');
      return;
    }

    try {
      console.log('[WebSocket] Connecting to:', this.url);
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => this.handleOpen();
      this.ws.onmessage = (event) => this.handleMessage(event);
      this.ws.onerror = (error) => this.handleError(error);
      this.ws.onclose = () => this.handleClose();
    } catch (error) {
      console.error('[WebSocket] Connection error:', error);
      this.scheduleReconnect();
    }
  }

  handleOpen() {
    console.log('[WebSocket] Connected successfully');
    this.isConnected = true;
    this.reconnectAttempts = 0;

    // Start heartbeat
    this.startHeartbeat();

    // Emit connection event
    this.emit('connected', { 
      timestamp: new Date().toISOString(),
      url: this.url 
    });

    // Process queued messages
    if (this.messageQueue.length > 0) {
      console.log(`[WebSocket] Processing ${this.messageQueue.length} queued messages`);
      while (this.messageQueue.length > 0) {
        const message = this.messageQueue.shift();
        this.send(message);
      }
    }
  }

  handleMessage(event) {
    try {
      const message = JSON.parse(event.data);
      const { type, payload, timestamp, entity_type, entity_id } = message;

      if (window.ENV?.DEBUG) {
        console.log('[WebSocket] Message received:', type, entity_type, entity_id);
      }

      // Emit specific event type
      if (type && type !== 'heartbeat') {
        this.emit(type, {
          ...payload,
          timestamp: timestamp || new Date().toISOString(),
          entity_type,
          entity_id,
          raw: message,
        });
      }

      // Emit generic message event
      this.emit('message', message);
    } catch (error) {
      console.error('[WebSocket] Message parse error:', error, event.data);
    }
  }

  handleError(error) {
    console.error('[WebSocket] Error:', error);
    this.emit('error', {
      timestamp: new Date().toISOString(),
      error: error.message || error,
    });
  }

  handleClose() {
    console.log('[WebSocket] Disconnected');
    this.isConnected = false;
    this.ws = null;
    this.stopHeartbeat();

    this.emit('disconnected', { timestamp: new Date().toISOString() });

    // Attempt reconnection
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.scheduleReconnect();
    } else {
      console.error('[WebSocket] Max reconnection attempts reached');
      this.emit('reconnect_failed', {
        attempts: this.reconnectAttempts,
        maxAttempts: this.maxReconnectAttempts,
        timestamp: new Date().toISOString(),
      });
    }
  }

  startHeartbeat() {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected) {
        try {
          this.ws.send(JSON.stringify({
            type: 'heartbeat',
            timestamp: new Date().toISOString(),
          }));
        } catch (error) {
          console.warn('[WebSocket] Heartbeat send failed:', error);
        }
      }
    }, this.heartbeatInterval);
  }

  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  scheduleReconnect() {
    this.reconnectAttempts++;
    // Exponential backoff with jitter
    const baseDelay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.maxReconnectDelay
    );
    const jitter = Math.random() * 1000; // 0-1s jitter
    const delay = baseDelay + jitter;

    console.log(
      `[WebSocket] Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${Math.round(delay)}ms`
    );

    this.emit('reconnecting', {
      attempt: this.reconnectAttempts,
      maxAttempts: this.maxReconnectAttempts,
      delayMs: delay,
      timestamp: new Date().toISOString(),
    });

    setTimeout(() => {
      this.connect();
    }, delay);
  }

  send(message) {
    if (!this.isConnected) {
      console.warn('[WebSocket] Not connected, queueing message:', message);
      this.messageQueue.push(message);
      return false;
    }

    try {
      this.ws.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error('[WebSocket] Send error:', error);
      return false;
    }
  }

  subscribe(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    const callbacks = this.listeners.get(eventType);
    if (!callbacks.includes(callback)) {
      callbacks.push(callback);
    }

    if (window.ENV?.DEBUG) {
      console.log(`[WebSocket] Subscribed to '${eventType}' (${callbacks.length} listeners)`);
    }

    // Return unsubscribe function
    return () => {
      this.unsubscribe(eventType, callback);
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
      if (window.ENV?.DEBUG) {
        console.log(`[WebSocket] Unsubscribed from '${eventType}' (${callbacks.length} listeners left)`);
      }
    }
  }

  emit(eventType, payload) {
    if (!this.listeners.has(eventType)) {
      return;
    }
    const callbacks = this.listeners.get(eventType);
    callbacks.forEach((callback) => {
      try {
        callback(payload);
      } catch (error) {
        console.error(`[WebSocket] Error in '${eventType}' listener:`, error);
      }
    });
  }

  disconnect() {
    this.stopHeartbeat();
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
      activeListeners: Array.from(this.listeners.keys()),
      listenerCounts: Object.fromEntries(
        Array.from(this.listeners.entries()).map(([type, cbs]) => [type, cbs.length])
      ),
      timestamp: new Date().toISOString(),
    };
  }
}

// Export singleton instance
export const wsManager = new WebSocketManager();

export default WebSocketManager;
