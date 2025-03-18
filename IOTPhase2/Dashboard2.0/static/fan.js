// fan.js
const fanImg = document.getElementById('fan');

// Set up the click event listener
fan.addEventListener('click', async () => {
    try {
        const response = await fetch('/toggle-fan');

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json(); // Assuming the server responds with JSON
        console.log('Fan toggled successfully:', data); // Handle response as needed
        
        // Update the fan image based on the fan status
        if (data.fan) {
            // we use the HTML part to retrieve the images. (to find it.)
            fanImg.src = fanOnUrl; // Use the variable defined in HTML
        } else {
            fanImg.src = fanUrl; // Use the variable defined in HTML
        }
        updateFanStatus(); // Optionally update the fan status after toggling
    } catch (error) {
        console.error('Error toggling fan:', error);
    }
});



// IMPORTANT: This method was made to update the fan status overtime  and via email (MAinly used when clicking on the email and replying yes. that way it will change the image based on the email and not the button.)

async function updateFanStatus() {
    try {
        const response = await fetch('/sensor-data');
        if (response.ok) {
            const data = await response.json();





            //const fanStatus = data.fan; // Get the fan status from the response
            //console.log('fanStatus: ' + fanStatus);

            //fanImg = document.getElementById('fan'); // Get the fan image element

            // Toggle spin class based on fan status (depreacted)
            if (data.fan) {
                fanImg.src = fanOnUrl; // Use the variable defined in HTML

               // fan.classList.add('spin'); // Add spin class to start spinning doesnt work..
            } else {
                fanImg.src = fanUrl; // Use the variable defined in HTML

                //fan.classList.remove('spin'); // Remove spin class to stop spinning doesnt work..
            }
        } else {
            console.error('Failed to fetch sensor data:', await response.text());
        }
    } catch (error) {
        console.error('Error fetching fan status:', error);
    }
}

// Fetch fan status every 5 seconds
setInterval(updateFanStatus, 5000);
updateFanStatus(); // Initial call to set fan status on load
