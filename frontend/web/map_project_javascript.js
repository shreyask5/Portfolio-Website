let map, service, infowindow, marker;

function initMap() {
map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 12.967308, lng: 77.587831},
    zoom: 12,
});

infowindow = new google.maps.InfoWindow({
    disableAutoPan: true,  // Disables auto-panning when opening the InfoWindow
    headerDisabled: true,  // This removes the "X" close button
});
marker = new google.maps.Marker({ map: map });

const input = document.getElementById("pac-input");
const autocomplete = new google.maps.places.Autocomplete(input, {
    fields: ["place_id", "geometry", "formatted_address", "name", "rating", "price_level", "user_ratings_total", "photos"]
});
autocomplete.bindTo("bounds", map);
map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

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

function displayPlaceDetails(place) {
const infowindowContent = document.getElementById("infowindow-content");
const ratingContent = document.getElementById("rating-content");
const starContainer = document.getElementById("star-rating");
const typeContainer = document.getElementById("type-content");

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
        return {
            converted_data: result.converted_data,
            wait_time: result.wait_time
        };
    } catch (error) {
        console.error('Error:', error.message);
        return null; // In case of error, return null or handle as needed
    }
}
const waitTimeData = getWaitTime(place);



infowindowContent.querySelector("#place-name").textContent = place.name || "Unknown";
ratingContent.querySelector("#place-rating").textContent = place.rating || "No rating";
typeContainer.querySelector("#waiting-time").textContent = waitTimeData.wait_time || "No waiting time data";
ratingContent.querySelector("#user_ratings_total").textContent = `(${place.user_ratings_total})`;
ratingContent.querySelector("#place-price-level").textContent = place.price_level ? `${"₹".repeat(place.price_level)}` : "No price info";

if (place.photos && place.photos.length > 0) {
    const photoUrl = place.photos[0].getUrl({maxWidth: 250});
    infowindowContent.querySelector("#place-photo").src = photoUrl;
} else {
    infowindowContent.querySelector("#place-photo").src = ""; // Default/fallback image
}

generateStars(place.rating, starContainer);

infowindow.setContent(infowindowContent);
infowindow.open(map, marker);
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

window.onload = initMap;