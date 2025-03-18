
async function updateHumidity() {
    try {
        const response = await fetch('/sensor-data');
        if (response.ok) {
            const data = await response.json();
            const humidity = data.humidity;

            
            document.getElementById('fu-percent').querySelector('span').innerText = humidity + '%';

            
            const humidityGaugeFill = document.getElementById('humidity-gauge__fill');
            humidityGaugeFill.style.height = humidity + '%'; 

            
            animatePercentChange(humidity, $('#fu-percent span'));
        } else {
            console.error('Failed to fetch humidity data:', await response.text());
        }
    } catch (error) {
        console.error('Error fetching humidity:', error);
    }
}


setInterval(updateHumidity, 5000);
updateHumidity(); 

var animatePercentChange = function animatePercentChange(newPercent, elem) {
    elem = elem || $('#fu-percent span');
    const val = parseInt(elem.text(), 10) || 0; 
    if (val !== parseInt(newPercent, 10)) {
        let diff = newPercent < val ? -1 : 1;
        elem.text(val + diff + '%'); 
        setTimeout(animatePercentChange.bind(null, newPercent, elem), 50); 
    }



};


