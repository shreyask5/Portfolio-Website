let map, service, infowindow, marker,busyChart; // Declare globally to keep track of the chart
const mobileWidth = window.matchMedia("(max-width: 37.5em)"); // 37.5em is 600px

function initMap() {
map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 12.967308, lng: 77.587831},
    zoom: 12,
});
infowindow = new google.maps.InfoWindow({
    disableAutoPan: true,  // Disables auto-panning when opening the InfoWindow
    headerDisabled: true,  // This removes the "X" close button
    minWidth: 200,
});
marker = new google.maps.Marker({ map: map });

const input = document.getElementById("pac-input");
const autocomplete = new google.maps.places.Autocomplete(input, {
    fields: ["place_id", "geometry", "formatted_address", "name", "rating", "price_level", "user_ratings_total", "photos"]
});
autocomplete.bindTo("bounds", map);
//To see if it's a phone or desktop

if (mobileWidth.matches) {
    // Mobile mode - push input to the left
    map.controls[google.maps.ControlPosition.LEFT].push(input);
} else {
    // Desktop mode - push input to the top left
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);
}

autocomplete.addListener("place_changed", () => {
    const place = autocomplete.getPlace();
    console.log(place.place_id)
    if (place.geometry && place.geometry.location) {
    map.setZoom(15);
    adjustMapCenterForInfoWindow(place.geometry.location, map, 200);
    marker.setPosition(place.geometry.location); // Update marker position
    marker.setVisible(true); // Ensure marker is visible
    displayPlaceDetails(place);
    }
});

map.addListener("click", (event) => {
    if (event.placeId) {
    getPlaceDetails(event.placeId);
    event.stop();
    }
});
}

//pushes the center down by 200px so it's easier too see
function adjustMapCenterForInfoWindow(location, map, offsetPx) {
const scale = Math.pow(2, map.getZoom());
const worldCoordinateCenter = map.getProjection().fromLatLngToPoint(location);
const pixelOffset = new google.maps.Point(0, offsetPx / scale);

const worldCoordinateNewCenter = new google.maps.Point(
    worldCoordinateCenter.x,
    worldCoordinateCenter.y - pixelOffset.y
);

const newCenter = map.getProjection().fromPointToLatLng(worldCoordinateNewCenter);
map.setCenter(newCenter);
}
function getPlaceDetails(placeId) {
service = new google.maps.places.PlacesService(map);
const request = {
    placeId: placeId,
    fields: ["place_id", "geometry.location", "formatted_address", "name", "rating", "price_level", "user_ratings_total", "photos"]
};
service.getDetails(request, (place, status) => {
    if (status === google.maps.places.PlacesServiceStatus.OK) {
    map.setZoom(15);
    adjustMapCenterForInfoWindow(place.geometry.location, map, 200);
    marker.setPosition(place.geometry.location); // Update marker position
    marker.setVisible(true); // Ensure marker is visible
    displayPlaceDetails(place);
    } else {
    console.error("Place details request failed: " + status);
    }
});
}

async function getWaitTime(place) {
    const placeId = place.place_id;
    const url = 'https://shreyask.in/projects/api2/'; // Update URL as per the server

    const data = {
        place_id: placeId
    };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        // Return an object containing both converted_data and wait_time
        console.log(result.wait_time)
        return {
            converted_data: result.converted_data,
            wait_time: result.wait_time
        };
    } catch (error) {
        console.error('Error:', error.message);
        return null; // In case of error, return null or handle as needed
    }
}

async function displayPlaceDetails(place) {
    const infowindowContent = document.getElementById("infowindow-content");
    const ratingContent = document.getElementById("rating-content");
    const starContainer = document.getElementById("star-rating");
    const typeContainer = document.getElementById("type-content");

    const waitTimeData = await getWaitTime(place);
    console.log(waitTimeData.wait_time)

    infowindowContent.querySelector("#place-name").textContent = place.name || "Unknown";
    ratingContent.querySelector("#place-rating").textContent = place.rating || "No rating";
    typeContainer.querySelector("#waiting-time").textContent = waitTimeData.wait_time || "No waiting time data";
    document.getElementById("waiting-time2").textContent = waitTimeData.wait_time || "No waiting time data";
    ratingContent.querySelector("#user_ratings_total").textContent = `(${place.user_ratings_total})`;
    ratingContent.querySelector("#place-price-level").textContent = place.price_level ? `${"₹".repeat(place.price_level)}` : "No price info";


    if (place.photos && place.photos.length > 0) {
        const width = 400;
        const height = 600; // Set your desired width
        for (let i = 0; i < 10; i++) {
            const photoUrl = place.photos[i].getUrl({
                maxWidth: width, 
                maxHeight: height // Correctly specify maxHeight here
            }); 
            // Directly access the image element using its ID
            const photoElement = document.getElementById("place-photo" + (i+1));
            
            // Check if the photo element exists before setting its src
            if (photoElement) {
                photoElement.src = photoUrl;
            } else {
                console.error("Element with id place-photo" + (i+1) + " not found.");
            }
        }
    } else {
        // Fallback if no photos exist
        const fallbackImage = document.getElementById("place-photo1"); // Assuming fallback for the first image
        if (fallbackImage) {
            fallbackImage.src = ""; // Set to some default image if desired
        }
    }

    generateStars(place.rating, starContainer);

    infowindow.setContent(infowindowContent);

    infowindow.open(map, marker);

    globalThis.chartData = waitTimeData.converted_data;
    console.log(chartData);
    const ctx = document.getElementById('busyChart').getContext('2d');

    displayPlaceDetailsGraph(chartData,ctx);
}

function generateStars(rating, starContainer) {
    starContainer.innerHTML = ""; // Clear previous stars
    const fullStarImg = "https://maps.gstatic.com/consumer/images/icons/2x/ic_star_rate_14.png";
    const halfStarImg = "https://maps.gstatic.com/consumer/images/icons/2x/ic_star_rate_half_14.png"
    const emptyStarImg = "https://my-portfolio-website-s3-bucket.s3.ap-south-1.amazonaws.com/assets/star_rating_blank_img.png";

    for (let i = 1; i <= 5; i++) {
        if (rating >= i) {
        const starImg = document.createElement("img");
        starImg.src = fullStarImg;
        starContainer.appendChild(starImg);
        } else if (rating >= i - 0.7) {
        const starImg = document.createElement("img");
        starImg.src = halfStarImg;
        starContainer.appendChild(starImg);
        }
    }
}

let slideIndex = 0;
let slideTimer;

// Start automatic slideshow
function showSlides() {
  let i;
  let slides = document.getElementsByClassName("mySlides");
  
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  
  slideIndex++;
  if (slideIndex > slides.length) {slideIndex = 1}
  
  slides[slideIndex-1].style.display = "block";

  slideTimer = setTimeout(showSlides, 4000); // Change image every 4 seconds
}

// Function to reset the timer after clicking next/previous
function plusSlides(n) {
  clearTimeout(slideTimer); // Stop the automatic slideshow
  slideIndex += n; // Increment or decrement the slide index
  if (slideIndex < 1) {slideIndex = document.getElementsByClassName("mySlides").length} // Loop back to the last slide
  if (slideIndex > document.getElementsByClassName("mySlides").length) {slideIndex = 1} // Loop back to the first slide
  showSlidesManually(); // Show the current slide and reset timer
}

// Function to manually display the slides and reset the timer
function showSlidesManually() {
  let i;
  let slides = document.getElementsByClassName("mySlides");

  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";  
  }

  if (slideIndex > slides.length) {slideIndex = 1}
  if (slideIndex < 1) {slideIndex = slides.length}

  slides[slideIndex-1].style.display = "block";   
  slideTimer = setTimeout(showSlides, 4000); // Restart the automatic slideshow
}

function displayPlaceDetailsGraph(chartData, ctx) {
    try {
        // Ensure ctx (chart context) exists
        if (!ctx) {
            throw new Error("Chart context (ctx) is missing or invalid.");
        }

        // Ensure chartData is valid
        if (!chartData || typeof chartData !== 'object' || Object.keys(chartData).length === 0) {
            busyChart.destroy();
        }

        // Check if the chart already exists and destroy it
        if (busyChart) {
            busyChart.destroy();
        }

        // Get today's day in 'DDD' format (e.g., 'Mon', 'Tue')
        const daysOfWeek = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
        const today = new Date();
        const dayName = daysOfWeek[today.getDay()];
        console.log(dayName);

        // Ensure chartData contains data for the current day
        if (!chartData[dayName]) {
            console.warn(`No data available for ${dayName}. Using empty dataset.`);
        }

        // Create the new chart
        manageDayButtons(chartData);
        window.busyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['12a', '1a', '2a', '3a', '4a', '5a', '6a', '7a', '8a', '9a', '10a', '11a', '12p', '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p', '10p', '11p'],
                datasets: [{
                    label: 'Waiting Time',
                    data: chartData[dayName], // Use empty array if no data for the current day
                    backgroundColor: 'rgba(249, 84, 84, 0.6)', // Change bar color
                    borderColor: 'rgba(249, 84, 84, 1)', // Change border color
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        min: 0, // Force y-axis to start at 0
                        max: 5, // Force y-axis to end at 5
                        ticks: {
                            stepSize: 1, // Ensure only 0, 1, 2, 3, 4, 5 are shown, no decimals
                            color: 'white', // Set tick color to white
                            font: {
                                size: 16 // Increase font size for y-axis labels (e.g., '10-20 min')
                            },
                            callback: function(value, index, values) {
                                // Customize the labels to display ranges
                                switch(value) {
                                    case 0: return '0-5 min';
                                    case 1: return '5-10 min';
                                    case 2: return '10-20 min';
                                    case 3: return '20-40 min';
                                    case 4: return '40-60 min';
                                    case 5: return '60-90 min';
                                    default: return ''; // Hide any other values (though max is 5)
                                }
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.2)' // Change grid line color to white with transparency
                        }
                    },
                    x: {
                        ticks: {
                            color: 'white', // Set tick color to white
                            font: {
                                size: 16 // Increase font size for x-axis labels
                            }
                        },
                        grid: {
                            display: false // Hide vertical grid lines
                        }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: 'white', // Set legend text color to white
                            font: {
                                size: 16 // Increase legend font size
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Waiting Time Chart',
                        color: 'white', // Set title color to white
                        font: {
                            size: 18 // Increase title font size
                        }
                    }
                }
            }
        });
        
        
        
    } catch (error) {
        console.error("Error in displayPlaceDetails:", error.message);
    }
}

function showChart(day) {
    try {
        // Ensure chartData exists and contains data for the requested day
        if (!chartData || !chartData[day]) {
            throw new Error(`No data available for the selected day: ${day}`);
        }

        // Ensure that busyChart has been initialized
        if (!window.busyChart) {
            throw new Error("Chart has not been initialized. Call displayPlaceDetailsGraph first.");
        }

        // Ensure datasets exist before trying to access them
        if (!window.busyChart.data || !window.busyChart.data.datasets || !window.busyChart.data.datasets[0]) {
            throw new Error("Chart data or datasets are not properly initialized.");
        }

        // Log the existing chart data for debugging
        console.log("Previous chart data: ", window.busyChart.data.datasets[0].data);

        // Update the chart data for the selected day
        window.busyChart.data.datasets[0].data = chartData[day] || [];
        window.busyChart.update();

        // Log the updated chart data for debugging
        console.log("Updated chart data: ", window.busyChart.data.datasets[0].data);

    } catch (error) {
        console.error("Error in showChart:", error.message);
    }
}

// Function to dynamically insert the buttons when chartData is available
function manageDayButtons(chartData) {
    const daySelector = document.querySelector('.day-selector');
    
    // Clear existing buttons (if any)
    daySelector.innerHTML = '';
    
    // If chartData is available, insert buttons
    if (chartData) {
        const days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
        
        days.forEach(day => {
            const button = document.createElement('button');
            button.textContent = day.charAt(0).toUpperCase() + day.slice(1); // Capitalize first letter
            button.onclick = () => showChart(day); // Assign the onclick event
            daySelector.appendChild(button); // Append button to div
        });
    }
}

// Call this function whenever chartData is updated
// For example, once chartData is loaded, you can call:
manageDayButtons(chartData[dayName]);  // or pass `null` if you want to remove buttons


window.onload = initMap;
showSlides();