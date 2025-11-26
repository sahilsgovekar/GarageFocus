// Web Worker for background timer functionality
// This runs independently of the main thread and isn't throttled when tab is inactive

let timerState = {
    isActive: false,
    startTime: null,
    duration: 0, // in minutes
    sessionId: null,
    mode: 'focus' // 'focus' or 'background'
};

let timerInterval = null;
let heartbeatInterval = null;

// Message handler from main thread
self.onmessage = function(e) {
    const { action, data } = e.data;
    
    switch (action) {
        case 'START_TIMER':
            startTimer(data);
            break;
        case 'STOP_TIMER':
            stopTimer();
            break;
        case 'GET_STATUS':
            sendStatus();
            break;
        case 'PAUSE_TIMER':
            pauseTimer();
            break;
        case 'RESUME_TIMER':
            resumeTimer();
            break;
    }
};

function startTimer({ duration, sessionId, mode = 'focus' }) {
    timerState = {
        isActive: true,
        startTime: Date.now(),
        duration: duration,
        sessionId: sessionId,
        mode: mode,
        pausedTime: 0
    };
    
    // Start the main timer loop
    timerInterval = setInterval(updateTimer, 1000);
    
    // Start heartbeat for server communication (every minute)
    heartbeatInterval = setInterval(sendHeartbeat, 60000);
    
    // Send initial status
    sendStatus();
    
    console.log(`Timer started: ${duration} minutes in ${mode} mode`);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    
    if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
        heartbeatInterval = null;
    }
    
    const elapsedMinutes = timerState.startTime ? 
        (Date.now() - timerState.startTime - (timerState.pausedTime || 0)) / 1000 / 60 : 0;
    
    timerState.isActive = false;
    
    // Send final status
    self.postMessage({
        type: 'TIMER_STOPPED',
        data: {
            elapsedMinutes: elapsedMinutes,
            wasActive: timerState.isActive
        }
    });
    
    console.log(`Timer stopped. Elapsed: ${elapsedMinutes.toFixed(1)} minutes`);
}

function pauseTimer() {
    if (!timerState.isActive) return;
    
    timerState.pausedAt = Date.now();
    
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    
    self.postMessage({
        type: 'TIMER_PAUSED'
    });
}

function resumeTimer() {
    if (!timerState.pausedAt) return;
    
    // Add the paused time to our total paused time
    timerState.pausedTime = (timerState.pausedTime || 0) + (Date.now() - timerState.pausedAt);
    delete timerState.pausedAt;
    
    // Restart the interval
    timerInterval = setInterval(updateTimer, 1000);
    
    self.postMessage({
        type: 'TIMER_RESUMED'
    });
}

function updateTimer() {
    if (!timerState.isActive || timerState.pausedAt) return;
    
    const now = Date.now();
    const elapsed = (now - timerState.startTime - (timerState.pausedTime || 0)) / 1000 / 60; // minutes
    const remaining = Math.max(0, timerState.duration - elapsed);
    
    // Send status update
    sendStatus();
    
    // Check if timer is complete
    if (remaining <= 0) {
        completeTimer();
    }
}

function completeTimer() {
    const elapsedMinutes = (Date.now() - timerState.startTime - (timerState.pausedTime || 0)) / 1000 / 60;
    
    stopTimer();
    
    self.postMessage({
        type: 'TIMER_COMPLETED',
        data: {
            elapsedMinutes: elapsedMinutes,
            success: true
        }
    });
}

function sendStatus() {
    if (!timerState.isActive) return;
    
    const now = Date.now();
    const elapsed = (now - timerState.startTime - (timerState.pausedTime || 0)) / 1000 / 60;
    const remaining = Math.max(0, timerState.duration - elapsed);
    
    self.postMessage({
        type: 'TIMER_UPDATE',
        data: {
            elapsed: elapsed,
            remaining: remaining,
            progress: elapsed / timerState.duration,
            duration: timerState.duration,
            mode: timerState.mode,
            isPaused: !!timerState.pausedAt
        }
    });
}

function sendHeartbeat() {
    if (!timerState.isActive) return;
    
    const elapsedMinutes = (Date.now() - timerState.startTime - (timerState.pausedTime || 0)) / 1000 / 60;
    
    self.postMessage({
        type: 'HEARTBEAT',
        data: {
            sessionId: timerState.sessionId,
            elapsedMinutes: elapsedMinutes,
            mode: timerState.mode
        }
    });
}

// Handle worker errors
self.onerror = function(error) {
    console.error('Timer worker error:', error);
    self.postMessage({
        type: 'WORKER_ERROR',
        data: { message: error.message }
    });
};

console.log('Timer worker initialized');
