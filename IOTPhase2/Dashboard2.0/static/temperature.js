
async function updateTemperature() {
    try {
        const response = await fetch('/sensor-data');
        if (response.ok) {
            const data = await response.json();
            const temperature = data.temperature;

     
            document.getElementById('gauge__cover').innerText = temperature + '°C';

           
            const gaugeFill = document.getElementById('gauge__fill');
            const percentage = (temperature / 40) * 100; 
            gaugeFill.style.height = percentage + '%'; 

           
            animateValue(temperature, $('#gauge__cover'));
        } else {
            console.error('Failed to fetch temperature data:', await response.text());
        }
    } catch (error) {
        console.error('Error fetching temperature:', error);
    }
}

setInterval(updateTemperature, 5000);
updateTemperature(); 

var animateValue = function animateValue(newPercent, elem) {
    elem = elem || $('#gauge__cover');
    const val = parseInt(elem.text(), 10) || 0; 
    if (val !== parseInt(newPercent, 10)) {
        let diff = newPercent < val ? -1 : 1;
        elem.text(val + diff + '°C'); 
        setTimeout(animateValue.bind(null, newPercent, elem), 50); 
    }




};
