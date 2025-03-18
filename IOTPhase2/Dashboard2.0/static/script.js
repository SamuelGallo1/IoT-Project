
async function updateSensorData() {
    try {
        const response = await fetch('/sensor-data');
        
    
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        
        const humidity = parseFloat(data.humidity);
        const temperature = parseFloat(data.temperature);

   
        if (isNaN(humidity) || isNaN(temperature)) {
            throw new Error('Invalid data received from the server.');
        }

        
        const humidityElement = document.getElementById('fu-percent');
        if (humidityElement) {
            humidityElement.querySelector('span').innerText = humidity + '%';
            const humidityGaugeFill = document.getElementById('humidity-gauge__fill');
            if (humidityGaugeFill) {
                humidityGaugeFill.style.height = humidity + '%';
            }
            animatePercentChange(humidity, $('#fu-percent span'));
        } else {
            console.warn('Humidity element not found in the DOM.');
        }

        // Update temperature
        const temperatureElement = document.getElementById('gauge__cover');
        if (temperatureElement) {
            temperatureElement.innerText = temperature + '°C';
            const gaugeFill = document.getElementById('gauge__fill');
            if (gaugeFill) {
                const percentage = (temperature / 40) * 100; 
                gaugeFill.style.height = percentage + '%';
            }
            animateValue(temperature, $('#gauge__cover'));
        } else {
            console.warn('Temperature element not found in the DOM.');
        }

    } catch (error) {
        console.error('Error fetching sensor data:', error);
    }
}


setInterval(updateSensorData, 5000);
updateSensorData(); 





