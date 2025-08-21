// Conexión WebSocket
const wsc1 = new WebSocket("ws://localhost:8000/ws/conteo_1");
wsc1.onmessage = function(event) {
    const [conteo_in, conteo_out ,predict_in, predict_out,car_in,car_out,
        bus_in,bus_out,truck_in,truck_out,conteo_g_in, conteo_g_out, is_running ] = event.data.split(',');

    document.getElementById("conteo_in").innerText = `${conteo_in}`;
    document.getElementById("conteo_out").innerText = `${conteo_out}`;
    document.getElementById("predict_in").innerText = `${predict_in}`;
    document.getElementById("predict_out").innerText = `${predict_out}`;
    document.getElementById("running").innerText = `${is_running}`;
    document.getElementById("car_in").innerText = `${car_in}`;
    document.getElementById("car_out").innerText = `${car_out}`;
    document.getElementById("bus_in").innerText = `${bus_in}`;
    document.getElementById("bus_out").innerText = `${bus_out}`;
    document.getElementById("truck_in").innerText = `${truck_in}`;
    document.getElementById("truck_out").innerText = `${truck_out}`;
    document.getElementById("conteo_g_in").innerText = `${conteo_g_in}`;
    document.getElementById("conteo_g_out").innerText = `${conteo_g_out}`;

};


const wsc2 = new WebSocket("ws://localhost:8000/ws/conteo_2");
// Actualizar el contenido del HTML cuando se recibe un mensaje del servidor
wsc2.onmessage = function(event) {
    const [conteo_n,conteo_s,conteo_e,conteo_o,
        conteo_global_na,conteo_global_sa,conteo_global_ea,conteo_global_oa ] = event.data.split(',');
    
    document.getElementById("conteo_n").innerText = `${conteo_n}`;
    document.getElementById("conteo_s").innerText = `${conteo_s}`;
    document.getElementById("conteo_e").innerText = `${conteo_e}`;
    document.getElementById("conteo_o").innerText = `${conteo_o}`;
    document.getElementById("conteo_golbal_na").innerText = `${conteo_global_na}`;
    document.getElementById("conteo_golbal_sa").innerText = `${conteo_global_sa}`;
    document.getElementById("conteo_golbal_ea").innerText = `${conteo_global_ea}`;
    document.getElementById("conteo_golbal_oa").innerText = `${conteo_global_oa}`;
   
};

const wsclima = new WebSocket("ws://localhost:8000/ws/clima");
// Actualizar el contenido del HTML cuando se recibe un mensaje del servidor
wsclima.onmessage = function(event) {
    const [des, temp, hum, vel, city,des1, temp2, hum3, vel4, city5] = event.data.split(',');
    document.getElementById("des").innerText = `${des}`;
    document.getElementById("temp").innerText = `${temp}`;
    document.getElementById("hum").innerText = `${hum}`;
    document.getElementById("vel").innerText = `${vel}`;
    document.getElementById("city").innerText = `${city}`;
    document.getElementById("dess").innerText = `${des1}`;
    document.getElementById("temps").innerText = `${temp2}`;
    document.getElementById("hums").innerText = `${hum3}`;
    document.getElementById("vels").innerText = `${vel4}`;
    document.getElementById("citys").innerText = `${city5}`;
};


async function startPrediction() {
            const res = await fetch('/start_prediction', { method: 'POST' });}

async function stopPrediction() {
            const res = await fetch('/stop_prediction', { method: 'POST' });}


// Función para mostrar la sección correspondiente
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
    });
    document.getElementById(sectionId).classList.remove('hidden');
}

function toggleSection(city) {
    const section = document.getElementById(city);
    const additionalSection = section.querySelector('.additional-section');
    const toggleButton = section.querySelector('.toggle-button');

    if (additionalSection.classList.contains('hidden')) {
        additionalSection.classList.remove('hidden');
        toggleButton.textContent = 'Mostrar conteo general';
    } else {
        additionalSection.classList.add('hidden');
        toggleButton.textContent = 'Mostrar conteo individual';
    }
}



// Inicialización del gráfico
// Inicialización del gráfico
const ctx = document.getElementById('trafficChart').getContext('2d'); // Renombrada para ser más simple
const maxDataPoints = 10; // Renombrada para ser más genérica

// Se ha cambiado "trafficChart_ind" por "trafficChart" para que coincida con el resto del código
const trafficChart = new Chart(ctx, { // <-- Error 1: Se usa la variable correcta 'ctx'
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'In',
            data: [],
            borderColor: '#2196F3',
            tension: 0.4,
            fill: false
        },
        {
            label: 'Out',
            data: [],
            borderColor: '#F44336',
            tension: 0.4,
            fill: false
        },{
            label: 'Predict_in',
            data: [],
            borderColor: '#5cff33',
            tension: 0.4,
            fill: false
        },{
            label: 'Predict_out',
            data: [],
            borderColor: '#5c3233',
            tension: 0.4,
            fill: false
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true
            }
        },
        animation: {
            duration: 750
        }
    }
});

// Función para actualizar el gráfico
function updateChart() {
    const conteoIn = parseInt(document.getElementById('conteo_g_in').textContent) || 0;
    const conteoOut = parseInt(document.getElementById('conteo_g_out').textContent) || 0;
    const predict_in = parseInt(document.getElementById('predict_in').textContent) || 0;
    const predict_out = parseInt(document.getElementById('predict_out').textContent) || 0;
    const currentTime = new Date().toLocaleTimeString();

    // Agregar nuevos datos
    // Error 2: Ahora "trafficChart" está definido y se puede usar aquí
    trafficChart.data.labels.push(currentTime);
    trafficChart.data.datasets[0].data.push(conteoIn);
    trafficChart.data.datasets[1].data.push(conteoOut);
    trafficChart.data.datasets[2].data.push(predict_in);
    trafficChart.data.datasets[3].data.push(predict_out);

    // Mantener solo los últimos 'maxDataPoints' puntos
    if (trafficChart.data.labels.length > maxDataPoints) { // Se usa la variable correcta
        trafficChart.data.labels.shift();
        trafficChart.data.datasets.forEach(dataset => dataset.data.shift());
    }

    trafficChart.update();
}

// Actualizar el gráfico cada 30.5 segundos
setInterval(updateChart, 300500);

// Primera actualización inmediata
updateChart();



// Inicialización del gráfico para Sevilla
const ctxSevilla = document.getElementById('trafficChart_sevilla').getContext('2d');
const maxDataPointsSevilla = 10;

const trafficChartSevilla = new Chart(ctxSevilla, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Norte',
            data: [],
            borderColor: '#2196F3',
            tension: 0.4,
            fill: false
        },
        {
            label: 'Sur',
            data: [],
            borderColor: '#F44336',
            tension: 0.4,
            fill: false
        },{
            label: 'Este',
            data: [],
            borderColor: '#5cff33',
            tension: 0.4,
            fill: false
        },{
            label: 'Oeste',
            data: [],
            borderColor: '#5c3233',
            tension: 0.4,
            fill: false
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true
            }
        },
        animation: {
            duration: 750
        }
    }
});

// Función para actualizar el gráfico de Sevilla
function updateChartSevilla() {
    const conteo_na = parseInt(document.getElementById('conteo_golbal_na').textContent);
    const conteo_sa = parseInt(document.getElementById('conteo_golbal_sa').textContent);
    const conteo_ea = parseInt(document.getElementById('conteo_golbal_ea').textContent);
    const conteo_oa = parseInt(document.getElementById('conteo_golbal_oa').textContent);
    const currentTime = new Date().toLocaleTimeString();

    trafficChartSevilla.data.labels.push(currentTime);
    trafficChartSevilla.data.datasets[0].data.push(conteo_na);
    trafficChartSevilla.data.datasets[1].data.push(conteo_sa);
    trafficChartSevilla.data.datasets[2].data.push(conteo_ea);
    trafficChartSevilla.data.datasets[3].data.push(conteo_oa);

    if (trafficChartSevilla.data.labels.length > maxDataPointsSevilla) {
        trafficChartSevilla.data.labels.shift();
        trafficChartSevilla.data.datasets.forEach(dataset => dataset.data.shift());
    }

    trafficChartSevilla.update();
}

// Actualizar el gráfico de Sevilla cada 10 segundos
setInterval(updateChartSevilla,  300500);

// Primera actualización inmediata para Sevilla
updateChartSevilla(); 







// Mostrar la página principal por defecto
document.addEventListener('DOMContentLoaded', function() {
    showSection('home');
});


