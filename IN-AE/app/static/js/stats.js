// app/static/js/stats.js

let charts = {};

function createChart(elementId, label, data, color) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    // Y축 설정을 센서 타입별로 구성합니다
    let yAxisConfig = {
        beginAtZero: false,
        // 기본 설정을 추가하여 일관성을 유지합니다
        grid: {
            color: 'rgba(0, 0, 0, 0.1)'
        }
    };

    // 각 센서 타입에 따라 적절한 범위를 설정합니다
    if (label.includes('Temp')) {
        yAxisConfig = {
            ...yAxisConfig,
            min: 0,   // 최저 온도 -10°C
            max: 40,    // 최고 온도 40°C
            ticks: {
                callback: value => `${value}°C`  // 온도 단위 표시
            }
        };
    } else if (label.includes('Humid')) {
        yAxisConfig = {
            ...yAxisConfig,
            min: 0,     // 최저 습도 0%
            max: 100,   // 최고 습도 100%
            ticks: {
                callback: value => `${value}%`   // 습도 단위 표시
            }
        };
    } else if (label.includes('Noise')) {
        yAxisConfig = {
            ...yAxisConfig,
            min: 0,     // 최저 소음 0dB
            max: 120,   // 최고 소음 120dB
            ticks: {
                callback: value => `${value}dB`  // 소음 단위 표시
            }
        };
    }

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.timestamps,
            datasets: [{
                label: label,
                data: data.values,
                borderColor: color,
                backgroundColor: color.replace(')', ', 0.1)'),
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: yAxisConfig,  // 수정된 Y축 설정 적용
                x: {
                    ticks: {
                        maxTicksLimit: 8
                    }
                }
            }
        }
    });
}
async function updateCharts() {
    try {
        // API에서 센서 데이터를 가져옵니다
        const response = await fetch('/admin/api/sensor-data');
        const sensorData = await response.json();
        
        // 시간순 정렬을 위해 데이터를 역순으로 배열합니다
        const reversedData = [...sensorData].reverse();
        
        // 타임스탬프와 센서값들을 포맷팅합니다
        const formattedData = {
            // 타임스탬프를 가독성 있는 시간 형식으로 변환
            timestamps: reversedData.map(d => {
                const [date, time] = d.timestamp.split('T');
                // date는 'YYYYMMDD' 형식
                const year = date.substring(0, 4);
                const month = date.substring(4, 6);
                const day = date.substring(6, 8);
                // time은 'HHmmss' 형식
                const hour = time.substring(0, 2);
                const minute = time.substring(2, 4);
                const second = time.substring(4, 6);
                const dateObj = new Date(year, month - 1, day, hour, minute, second);
                return dateObj.toLocaleTimeString();
            }),
            // 각 센서 데이터를 배열로 추출
            temperature: reversedData.map(d => d.temperature),
            humidity: reversedData.map(d => d.humidity),
            noise: reversedData.map(d => d.noise_level)
        };

        // 현재 센서값을 UI에 표시 (가장 최신 데이터 사용)
        if (sensorData.length > 0) {
            const latest = sensorData[0];
            document.getElementById('currentTemp').textContent = `${latest.temperature.toFixed(1)}°C`;
            document.getElementById('currentHumid').textContent = `${latest.humidity.toFixed(1)}%`;
            document.getElementById('currentNoise').textContent = `${latest.noise_level.toFixed(1)}dB`;
        }

        // 온도 차트 업데이트 또는 생성
        if (!charts.temperature) {
            // 차트가 없으면 새로 생성
            charts.temperature = createChart('temperatureChart', 'Temperature (°C)', 
                {timestamps: formattedData.timestamps, values: formattedData.temperature},
                'rgb(255, 99, 132)');
        } else {
            // 기존 차트 데이터 업데이트
            charts.temperature.data.labels = formattedData.timestamps;
            charts.temperature.data.datasets[0].data = formattedData.temperature;
            charts.temperature.update();
        }

        // 습도 차트 업데이트 또는 생성
        if (!charts.humidity) {
            charts.humidity = createChart('humidityChart', 'Humid (%)', 
                {timestamps: formattedData.timestamps, values: formattedData.humidity},
                'rgb(54, 162, 235)');
        } else {
            charts.humidity.data.labels = formattedData.timestamps;
            charts.humidity.data.datasets[0].data = formattedData.humidity;
            charts.humidity.update();
        }

        // 소음 차트 업데이트 또는 생성
        if (!charts.noise) {
            charts.noise = createChart('noiseChart', 'Noise (dB)', 
                {timestamps: formattedData.timestamps, values: formattedData.noise},
                'rgb(75, 192, 192)');
        } else {
            charts.noise.data.labels = formattedData.timestamps;
            charts.noise.data.datasets[0].data = formattedData.noise;
            charts.noise.update();
        }
    } catch (error) {
        console.error('Error fetching sensor data:', error);
    }
}


document.addEventListener('DOMContentLoaded', () => {
    initializeControls();  // 컨트롤 초기화
    updateCharts();        // 기존 차트 업데이트 함수
    setInterval(updateCharts, 60000); // 1분마다 차트 업데이트
});

let updateTimeout = null;

function initializeControls() {
    const hue = parseInt(document.getElementById('hueValue').innerText.slice(0, -1));
    const saturation = parseInt(document.getElementById('saturationValue').innerText.slice(0, -1));
    const lightness = parseInt(document.getElementById('lightnessValue').innerText.slice(0, -1));
    const lux = parseInt(document.getElementById('luxValue').innerText);
    
    // 슬라이더 값 설정
    document.getElementById('hueSlider').value = hue;
    document.getElementById('saturationSlider').value = saturation;
    document.getElementById('lightnessSlider').value = lightness;
    document.getElementById('luxSlider').value = lux;
    
    // 초기 색상 미리보기 설정 - 이 부분이 추가됨
    const initialHslColor = `hsl(${hue}, ${saturation}%, ${lightness}%)`;
    document.getElementById('colorPreview').style.backgroundColor = initialHslColor;
    document.getElementById('colorValues').textContent = initialHslColor;
    function updateColor() {
        const hue = document.getElementById('hueSlider').value;
        const saturation = document.getElementById('saturationSlider').value;
        const lightness = document.getElementById('lightnessSlider').value;
        const lux = document.getElementById('luxSlider').value;

        // 값 표시 업데이트
        document.getElementById('hueValue').textContent = `${hue}°`;
        document.getElementById('saturationValue').textContent = `${saturation}%`;
        document.getElementById('lightnessValue').textContent = `${lightness}%`;
        document.getElementById('luxValue').textContent = lux;

        // HSL 색상 문자열 생성
        const hslColor = `hsl(${hue}, ${saturation}%, ${lightness}%)`;
        
        // 색상 미리보기 업데이트
        document.getElementById('colorPreview').style.backgroundColor = hslColor;
        document.getElementById('colorValues').textContent = hslColor;

        // 디바운싱을 적용하여 서버 요청 최적화
        clearTimeout(updateTimeout);
        updateTimeout = setTimeout(() => {
            fetch('/admin/api/update-lighting', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    hue: parseInt(hue),
                    saturation: parseInt(saturation),
                    lightness: parseInt(lightness),
                    lux: parseInt(lux)
                })
            }).catch(error => console.error('Update fail:', error));
        }, 300);  // 300ms 디바운스 타임아웃
    }

    // 슬라이더 이벤트 리스너 등록
    const sliders = ['hueSlider', 'saturationSlider', 'lightnessSlider', 'luxSlider'];
    sliders.forEach(id => {
        document.getElementById(id).addEventListener('input', updateColor);
    });
}
// DOM 로드 시 초기화 함수에 컨트롤 초기화 추가
