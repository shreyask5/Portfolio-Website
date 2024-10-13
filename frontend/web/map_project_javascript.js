let map, service, infowindow, marker;
let busyChart; // Declare globally to track the chart instance
const mobileWidth = window.matchMedia("(max-width: 37.5em)"); // 37.5em is 600px
const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']; // Get today's day in DDD format
const today = new Date();
let dayName = daysOfWeek[today.getDay()];

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: 12.967308, lng: 77.587831 },
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

    // Push input to the correct location depending on device type
    if (mobileWidth.matches) {
        map.controls[google.maps.ControlPosition.LEFT].push(input);
    } else {
        map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);
    }

    autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();
        console.log(place.place_id);
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

// Adjusts the map center down by offsetPx for better InfoWindow visibility
function adjustMapCenterForInfoWindow(location, map, offsetPx) {
    if (!map.getProjection()) {
        console.error('Map projection not loaded yet.');
        return;
    }
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

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const result = await response.json();

        // Return an object containing both converted_data and wait_time
        console.log(result.wait_time);
        return {
            converted_data: result.converted_data,
            wait_time: result.wait_time
        };
    } catch (error) {
        console.error('Error:', error.message);
        alert('Failed to retrieve wait time. Please try again later.');
        return null; // In case of error, return null or handle as needed
    }
}

async function displayPlaceDetails(place) {
    const infowindowContent = document.getElementById("infowindow-content");
    const ratingContent = document.getElementById("rating-content");
    const starContainer = document.getElementById("star-rating");
    const typeContainer = document.getElementById("type-content");

    const waitTimeData = await getWaitTime(place);
    if (!waitTimeData) {
        return; // Exit if there is an error in fetching wait time data
    }

    infowindowContent.querySelector("#place-name").textContent = place.name || "Unknown";
    ratingContent.querySelector("#place-rating").textContent = place.rating || "No rating";
    typeContainer.querySelector("#waiting-time").textContent = waitTimeData.wait_time || "No waiting time data";
    document.getElementById("waiting-time2").textContent = waitTimeData.wait_time || "No waiting time data";
    ratingContent.querySelector("#user_ratings_total").textContent = `(${place.user_ratings_total})`;
    ratingContent.querySelector("#place-price-level").textContent = place.price_level ? `${"₹".repeat(place.price_level)}` : "No price info";

    // Load and display photos
    if (place.photos && place.photos.length > 0) {
        const width = 400;
        const height = 600;
        for (let i = 0; i < 10; i++) {
            const photoUrl = place.photos[i]?.getUrl({
                maxWidth: width,
                maxHeight: height
            }) || 'path_to_fallback_image.jpg'; // Fallback image
            const photoElement = document.getElementById("place-photo" + (i + 1));
            if (photoElement) {
                photoElement.src = photoUrl;
            } else {
                console.error("Element with id place-photo" + (i + 1) + " not found.");
            }
        }
    } else {
        // Fallback if no photos exist
        const fallbackImage = document.getElementById("place-photo1");
        if (fallbackImage) {
            fallbackImage.src = 'path_to_fallback_image.jpg'; // Set to some default image
        }
    }

    generateStars(place.rating, starContainer);

    infowindow.setContent(infowindowContent);
    infowindow.open(map, marker);

    const chartData = waitTimeData.converted_data;
    const ctx = document.getElementById('busyChart').getContext('2d');
    displayChartDetails(chartData, ctx); // Display chart data
}

function generateStars(rating, starContainer) {
    starContainer.innerHTML = ""; // Clear previous stars
    const fullStarImg = "https://maps.gstatic.com/consumer/images/icons/2x/ic_star_rate_14.png";
    const halfStarImg = "https://maps.gstatic.com/consumer/images/icons/2x/ic_star_rate_half_14.png";
    const emptyStarImg = "https://my-portfolio-website-s3-bucket.s3.ap-south-1.amazonaws.com/assets/star_rating_blank_img.png";

    for (let i = 1; i <= 5; i++) {
        const starImg = document.createElement("img");
        if (rating >= i) {
            starImg.src = fullStarImg;
        } else if (rating >= i - 0.7) {
            starImg.src = halfStarImg;
        } else {
            starImg.src = emptyStarImg;
        }
        starContainer.appendChild(starImg);
    }
}

// Display chart data and update chart
function displayChartDetails(chartData, ctx) {
    if (busyChart) {
        busyChart.destroy(); // Destroy the existing chart
    }
    busyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['12a', '1a', '2a', '3a', '4a', '5a', '6a', '7a', '8a', '9a', '10a', '11a', '12p', '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p', '10p', '11p'],
            datasets: [{
                label: 'Waiting Time',
                data: chartData[dayName], // Default data for current day
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Slideshow controls
let slideIndex = 1;
showSlides(slideIndex);

function plusSlides(n) {
    clearTimeout(slideTimer); // Clear automatic slideshow timer when manually switching slides
    slideIndex += n;

    const slides = document.getElementsByClassName("mySlides");
    if (slideIndex < 1) {
        slideIndex = slides.length;
    }
    if (slideIndex > slides.length) {
        slideIndex = 1;
    }

    showSlidesManually();
}

function showSlidesManually() {
    const slides = document.getElementsByClassName("mySlides");
    for (let i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    slides[slideIndex - 1].style.display = "block";
}
