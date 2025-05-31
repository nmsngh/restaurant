// 차트 객체를 저장할 맵
const charts = new Map();

// 차트 생성 함수
function createChart(restaurantId, data) {
    const ctx = document.getElementById(`tempChart-${restaurantId}`).getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.timestamps.map(t => {
                const date = new Date(
                    t.slice(0,4), 
                    t.slice(4,6)-1, 
                    t.slice(6,8), 
                    t.slice(9,11), 
                    t.slice(11,13), 
                    t.slice(13,15)
                );
                return date.toLocaleTimeString();
            }),
            datasets: [{
                label: '온도 (°C)',
                data: data.temperature,
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: '최근 온도 변화'
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
    
    return chart;
}

// 실시간 데이터 업데이트
async function updateRealtimeData(restaurantId) {
    try {
        const response = await fetch(`/admin/api/restaurant/${restaurantId}/sensor-data?duration=24h`);
        const data = await response.json();
        
        // 실시간 값 업데이트
        if (data.temperature.length > 0) {
            document.getElementById(`temp-${restaurantId}`).textContent = 
                data.temperature[data.temperature.length - 1].toFixed(1);
            document.getElementById(`humid-${restaurantId}`).textContent = 
                data.humidity[data.humidity.length - 1].toFixed(1);
            document.getElementById(`noise-${restaurantId}`).textContent = 
                data.noise_level[data.noise_level.length - 1].toFixed(1);
        }
        
        // 차트 업데이트
        let chart = charts.get(restaurantId);
        if (!chart) {
            chart = createChart(restaurantId, data);
            charts.set(restaurantId, chart);
        } else {
            chart.data.labels = data.timestamps.map(t => {
                const date = new Date(
                    t.slice(0,4), 
                    t.slice(4,6)-1, 
                    t.slice(6,8), 
                    t.slice(9,11), 
                    t.slice(11,13), 
                    t.slice(13,15)
                );
                return date.toLocaleTimeString();
            });
            chart.data.datasets[0].data = data.temperature;
            chart.update();
        }
    } catch (error) {
        console.error('Error fetching sensor data:', error);
    }
}

// 상세 통계 페이지의 차트 생성
function createStatsCharts(restaurantId, data) {
    // 온도 차트
    const tempCtx = document.getElementById('temperatureChart').getContext('2d');
    new Chart(tempCtx, {
        type: 'line',
        data: {
            labels: data.timestamps.map(t => {
                const date = new Date(
                    t.slice(0,4), 
                    t.slice(4,6)-1, 
                    t.slice(6,8), 
                    t.slice(9,11), 
                    t.slice(11,13), 
                    t.slice(13,15)
                );
                return date.toLocaleString();
            }),
            datasets: [{
                label: '온도 (°C)',
                data: data.temperature,
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: '온도 변화 그래프'
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });

    // 습도 차트
    const humidCtx = document.getElementById('humidityChart').getContext('2d');
    new Chart(humidCtx, {
        type: 'line',
        data: {
            labels: data.timestamps.map(t => {
                const date = new Date(
                    t.slice(0,4), 
                    t.slice(4,6)-1, 
                    t.slice(6,8), 
                    t.slice(9,11), 
                    t.slice(11,13), 
                    t.slice(13,15)
                );
                return date.toLocaleString();
            }),
            datasets: [{
                label: '습도 (%)',
                data: data.humidity,
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: '습도 변화 그래프'
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });

    // 소음 차트
    const noiseCtx = document.getElementById('noiseChart').getContext('2d');
    new Chart(noiseCtx, {
        type: 'line',
        data: {
            labels: data.timestamps.map(t => {
                const date = new Date(
                    t.slice(0,4), 
                    t.slice(4,6)-1, 
                    t.slice(6,8), 
                    t.slice(9,11), 
                    t.slice(11,13), 
                    t.slice(13,15)
                );
                return date.toLocaleString();
            }),
            datasets: [{
                label: '소음 레벨 (dB)',
                data: data.noise_level,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: '소음 레벨 변화 그래프'
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', function() {
    // 대시보드의 경우
    if (typeof restaurants !== 'undefined') {
        // 각 레스토랑의 데이터를 주기적으로 업데이트
        restaurants.forEach(id => {
            updateRealtimeData(id);
            setInterval(() => updateRealtimeData(id), 60000); // 1분마다 업데이트
        });
    }

    // 상세 통계 페이지의 경우
    const statsContainer = document.getElementById('statsCharts');
    if (statsContainer) {
        const restaurantId = statsContainer.dataset.restaurantId;
        fetch(`/admin/api/restaurant/${restaurantId}/sensor-data?duration=24h`)
            .then(response => response.json())
            .then(data => createStatsCharts(restaurantId, data))
            .catch(error => console.error('Error:', error));
    }
});