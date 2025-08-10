import { useEffect, useRef, useState } from 'react';
import { io } from 'socket.io-client';

export const useSocket = (serverUrl = 'http://localhost:5000') => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const socketRef = useRef(null);
  const maxReconnectAttempts = 5;

  useEffect(() => {
    // Create socket connection
    socketRef.current = io(serverUrl, {
      transports: ['websocket', 'polling'],
      timeout: 30000,
      reconnection: true,
      reconnectionDelay: 2000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: maxReconnectAttempts,
      autoConnect: true,
      forceNew: false,
      upgrade: true,
      rememberUpgrade: true
    });

    const socket = socketRef.current;

    // Connection event handlers
    socket.on('connect', () => {
      console.log('✅ WebSocket connected to backend');
      setIsConnected(true);
      setConnectionError(null);
      setReconnectAttempts(0);
    });

    // Test event listeners for debugging
    socket.on('connection_confirmed', (data) => {
      console.log('🎉 WebSocket connection confirmed:', data.message);
    });



    // Note: card_generated events are handled by components via onCardGenerated subscription
    // We log here just for debugging but don't process the data to avoid conflicts
    socket.on('card_generated', (data) => {
      console.log('🃏 WebSocket card_generated event received in useSocket hook:', data.card.name);
      console.log('🔍 Event data structure:', data);
    });

    socket.on('disconnect', (reason) => {
      console.log('❌ WebSocket disconnected from backend:', reason);
      setIsConnected(false);
      if (reason === 'io server disconnect') {
        // Server forcefully disconnected, client won't automatically reconnect
        setConnectionError('Server disconnected the connection');
      }
    });

    socket.on('connect_error', (error) => {
      console.error('❌ WebSocket connection error:', error);
      setIsConnected(false);
      
      // Better error message based on error type
      let errorMessage = 'Connection failed';
      if (error.message) {
        errorMessage = error.message;
      } else if (error.description) {
        errorMessage = error.description;
      } else if (error.type === 'TransportError') {
        errorMessage = 'Network transport error - check if backend is running';
      } else if (error.type === 'TimeoutError') {
        errorMessage = 'Connection timeout - backend may be overloaded';
      }
      
      setConnectionError(errorMessage);
      
      // Increment reconnect attempts
      setReconnectAttempts(prev => {
        const newAttempts = prev + 1;
        if (newAttempts >= maxReconnectAttempts) {
          console.error(`❌ Max reconnection attempts (${maxReconnectAttempts}) reached`);
          setConnectionError(`Failed to connect after ${maxReconnectAttempts} attempts: ${errorMessage}`);
        }
        return newAttempts;
      });
    });

    socket.on('reconnect', (attemptNumber) => {
      console.log(`🔄 WebSocket reconnected after ${attemptNumber} attempts`);
      setConnectionError(null);
      setReconnectAttempts(0);
    });

    socket.on('reconnect_error', (error) => {
      console.error('❌ WebSocket reconnection error:', error);
      setConnectionError('Reconnection failed');
    });

    // Cleanup on unmount
    return () => {
      console.log('🧹 Cleaning up WebSocket connection');
      socket.disconnect();
    };
  }, [serverUrl]);

  // Function to subscribe to card generation events
  const onCardGenerated = (callback) => {
    if (socketRef.current) {
      socketRef.current.on('card_generated', callback);
      console.log('👂 Subscribed to card_generated events with callback:', callback.name || 'anonymous');
    }
  };

  // Function to unsubscribe from card generation events
  const offCardGenerated = (callback) => {
    if (socketRef.current) {
      socketRef.current.off('card_generated', callback);
      console.log('🔇 Unsubscribed from card_generated events with callback:', callback.name || 'anonymous');
    }
  };

  // Function to subscribe to batch completion events
  const onBatchCompleted = (callback) => {
    if (socketRef.current) {
      socketRef.current.on('batch_completed', callback);
      console.log('👂 Subscribed to batch_completed events');
    }
  };

  // Function to unsubscribe from batch completion events
  const offBatchCompleted = (callback) => {
    if (socketRef.current) {
      socketRef.current.off('batch_completed', callback);
      console.log('🔇 Unsubscribed from batch_completed events');
    }
  };

  // Function to manually reconnect
  const reconnect = () => {
    if (socketRef.current && !isConnected) {
      console.log('🔄 Manually attempting to reconnect WebSocket...');
      setReconnectAttempts(0);
      setConnectionError(null);
      socketRef.current.connect();
    }
  };



  return {
    socket: socketRef.current,
    isConnected,
    connectionError,
    reconnectAttempts,
    maxReconnectAttempts,
    reconnect,
    onCardGenerated,
    offCardGenerated,
    onBatchCompleted,
    offBatchCompleted
  };
};
