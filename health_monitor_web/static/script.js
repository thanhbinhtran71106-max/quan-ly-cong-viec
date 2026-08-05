// Cập nhật Đồng hồ
function updateClock() {
    const now = new Date();
    document.getElementById('clock').textContent = now.toLocaleTimeString('vi-VN');
}
setInterval(updateClock, 1000);
updateClock();

// Chart.js Configuration
const ctx = document.getElementById('ecgChart').getContext('2d');
const maxDataPoints = 150;
const labels = Array.from({length: maxDataPoints}, (_, i) => '');
const ecgData = Array.from({length: maxDataPoints}, () => 0);

const ecgChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: labels,
        datasets: [{
            data: ecgData,
            borderColor: '#10b981',
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.3,
            fill: false,
        }]
    },
    options: {
        responsive: true, maintainAspectRatio: false,
        animation: { duration: 0 },
        scales: {
            x: { display: false },
            y: { display: true, min: 0, max: 4095, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
        },
        plugins: { legend: { display: false }, tooltip: { enabled: false } }
    }
});

// Toast Logic
let lastAlertTime = 0;
function showToast(title, message) {
    const now = Date.now();
    if (now - lastAlertTime < 5000) return; // Tránh spam toast liên tục mỗi 5s
    lastAlertTime = now;

    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        <div class="toast-content">
            <h4>${title}</h4>
            <p>${message}</p>
        </div>
    `;
    container.appendChild(toast);
    
    // Auto remove sau 5s
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Check Thresholds
const THRESHOLDS = {
    bpmHigh: 120,
    bpmLow: 50,
    spo2Low: 94
};

function checkVitals(bpm, spo2) {
    const bpmCard = document.getElementById('card-bpm');
    const spo2Card = document.getElementById('card-spo2');

    if (bpm > THRESHOLDS.bpmHigh || bpm < THRESHOLDS.bpmLow) {
        bpmCard.classList.add('danger');
        showToast("Cảnh báo Nhịp tim!", `Nhịp tim hiện tại (${bpm} bpm) đang ở mức nguy hiểm.`);
    } else {
        bpmCard.classList.remove('danger');
    }

    if (spo2 < THRESHOLDS.spo2Low) {
        spo2Card.classList.add('danger');
        showToast("Cảnh báo Oxy máu!", `SpO2 giảm xuống mức ${spo2}%. Cần kiểm tra hô hấp ngay.`);
    } else {
        spo2Card.classList.remove('danger');
    }
}

// WebSocket Connection
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${wsProtocol}//${window.location.host}/ws`;
let ws;

function connectWebSocket() {
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        document.getElementById('connection-status').classList.add('connected');
        document.getElementById('status-text').textContent = 'Live System (Connected)';
    };

    ws.onclose = () => {
        document.getElementById('connection-status').classList.remove('connected');
        document.getElementById('status-text').textContent = 'Disconnected...';
        setTimeout(connectWebSocket, 3000);
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            
            if (data.bpm) {
                document.getElementById('bpm-val').textContent = data.bpm;
                if(data.spo2) checkVitals(data.bpm, data.spo2);
            }
            if (data.spo2) document.getElementById('spo2-val').textContent = data.spo2;
            if (data.body_temp) document.getElementById('body-temp-val').textContent = data.body_temp.toFixed(1);
            if (data.room_temp) document.getElementById('room-temp-val').textContent = data.room_temp.toFixed(1) + "°C";
            if (data.humidity) document.getElementById('humidity-val').textContent = data.humidity.toFixed(0) + "%";

            if (data.ecg !== undefined) {
                ecgChart.data.datasets[0].data.shift();
                ecgChart.data.datasets[0].data.push(data.ecg);
                ecgChart.update('none');
            }
        } catch (e) {}
    };
}
connectWebSocket();

// Export Function
async function exportData() {
    try {
        const response = await fetch('/api/export');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `patient_data_${new Date().toISOString().slice(0,10)}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } else {
            alert("Lỗi khi tải file export.");
        }
    } catch (e) {
        console.error("Export error", e);
        alert("Server chưa sẵn sàng để xuất dữ liệu.");
    }
}
