Cesium.Ion.defaultAccessToken = CESIUM_KEY


const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent) || window.innerWidth < 768;

const viewer = new Cesium.Viewer('cesiumContainer', {
    terrain: Cesium.Terrain.fromWorldTerrain({
      requestVertexNormals: true,
    }),
    animation: false,
    timeline: false,
    baseLayerPicker: false,
    geocoder: false,
    homeButton: false,
    navigationHelpButton: false,
    sceneModePicker: false,
    fullscreenButton: false,
    allowPicking: false,
    msaaSamples: isMobile ? 1 : 4,
    useBrowserRecommendedResolution: isMobile ? true : false
});

viewer.camera.setView({
    destination: Cesium.Cartesian3.fromDegrees(-103, 34, 5999999),
    orientation: {
        heading: Cesium.Math.toRadians(0.0),
        pitch: Cesium.Math.toRadians(-90),
        roll: 0.0
    }
});

viewer.scene.screenSpaceCameraController._zoomFactor = 4.0;
viewer.cesiumWidget.creditContainer.style.display = 'none';
viewer.scene.globe.baseColor = Cesium.Color.fromCssColorString('#1a1a1a');
viewer.scene.backgroundColor = Cesium.Color.fromCssColorString('#0f0f0f');

viewer.screenSpaceEventHandler.setInputAction(function(click) {
    const cartesian = viewer.scene.pickPosition(click.position);
}, Cesium.ScreenSpaceEventType.LEFT_CLICK);


// Area Pins
const climbingAreas = [
    { name: "Joshua Tree NP", coords: [-116.16795, 34.0122, 1000], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Tahquitz & Suicide", coords: [-116.679, 33.7607, 2351], font: "14pt monospace", minDistance: 20000.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Tahquitz Rock", coords: [-116.68322, 33.76025, 2400], font: "14pt monospace", minDistance: 0, maxDistanceText: 20000.0, maxDistance: 20000.0 },
    { name: "Suicide Rock", coords: [-116.69415, 33.77004, 2100], font: "14pt monospace", minDistance: 0, maxDistanceText: 20000.0, maxDistance: 20000.0 },
    { name: "Yosemite Valley", coords: [-119.63452, 37.72349, 1200], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Squamish", coords: [-123.15393, 49.67997, 20], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Indian Creek", coords: [-109.53987, 38.02574, 1757], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Red Rocks", coords: [-115.42451, 36.13128, 1127], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Smith Rock", coords: [-121.13906, 44.36779, 992], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Tuolumne Meadows", coords: [-119.35782, 37.87401, 2600], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 2000000.0 },
    { name: "Vedauwoo", coords: [-105.37821, 41.18479, 2030], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Ten Sleep Canyon", coords: [-107.24497, 44.13869, 1350], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Devils Tower", coords: [-104.71507, 44.59048, 1584], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Red River Gorge", coords: [-83.68217, 37.67745, 250], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "New River Gorge", coords: [-81.06337, 38.07788, 300], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Rumney", coords: [-71.8367, 43.8021, 300], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Shawangunks", coords: [-74.20173, 41.65146, 300], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "The Needles", coords: [-118.50838, 36.11985, 1100], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Bishop", coords: [-118.39539, 37.36119, 1210], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Lover's Leap", coords: [-120.14053, 38.79949, 1200], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Index", coords: [-121.56191, 47.82481, 150], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Eldorado Canyon", coords: [-105.28121, 39.9318, 1600], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Wasatch Range", coords: [-111.72869, 40.60538, 2000], font: "14pt monospace", minDistance: 20000.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Little Cottonwood Canyon", coords: [-111.77699, 40.5727, 1950], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 20000.0, maxDistance: 20000.0 },
    { name: "Big Cottonwood Canyon", coords: [-111.789, 40.6193, 1900], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 20000.0, maxDistance: 20000.0 },
    { name: "City of Rocks", coords: [-113.72398, 42.0778, 1800], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Rifle", coords: [-107.6912, 39.7159, 1600], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 },
    { name: "Saint George", coords: [-113.59297, 37.05079, 960], font: "14pt monospace", minDistance: 0.0, maxDistanceText: 2000000.0, maxDistance: 8000000.0 }
];

climbingAreas.forEach(area => {
    viewer.entities.add({
        name: area.name,
        position: Cesium.Cartesian3.fromDegrees(...area.coords),
        point: {
            pixelSize: 5,
            color: Cesium.Color.BLACK,
            outlineColor: Cesium.Color.WHITE,
            outlineWidth: 2,
            distanceDisplayCondition: new Cesium.DistanceDisplayCondition(area.minDistance, area.maxDistance),
            heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
        },
        label: {
            text: area.name,
            font: area.font,
            style: Cesium.LabelStyle.FILL_AND_OUTLINE,
            outlineColor: Cesium.Color.GRAY,
            fillColor: Cesium.Color.BLACK,
            outlineWidth: 2,
            verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
            pixelOffset: new Cesium.Cartesian2(0, -10),
            heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
            distanceDisplayCondition: new Cesium.DistanceDisplayCondition(area.minDistance, area.maxDistanceText)
        }
    })
});



// Variable to store the current point
let currentPoint = null;

function createPoint(worldPosition) {
    if (currentPoint) {
        viewer.entities.remove(currentPoint);
    }

    currentPoint = viewer.entities.add({
        position: worldPosition,
        billboard: {
            image: PIN_ICON,
            width: 32,
            height: 48,
            pixelOffset: new Cesium.Cartesian2(0, -15),
            scale: 0.65,
            heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
        },
    });

    const submitContainer = document.getElementById('submitContainer');
    if (submitContainer) {
        submitContainer.classList.add('visible');
    }

    return currentPoint;
}

const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

handler.setInputAction(function (click) {
    const ray = viewer.camera.getPickRay(click.position);

    const cartesian = viewer.scene.globe.pick(ray, viewer.scene);

    if (cartesian) {
        createPoint(cartesian);

        const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
        const longitude = Cesium.Math.toDegrees(cartographic.longitude);
        const latitude = Cesium.Math.toDegrees(cartographic.latitude);
        console.log(`Clicked at: Lon ${longitude.toFixed(4)}, Lat ${latitude.toFixed(4)}`);
    }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK);

const menuToggle = document.getElementById('menuToggle');
const menuOptions = document.getElementById('menuOptions');
const mapControlsMenu = document.getElementById('mapControlsMenu');
let isMenuOpen = false;

menuToggle.addEventListener('click', function(e) {
    e.stopPropagation();
    isMenuOpen = !isMenuOpen;
    mapControlsMenu.classList.toggle('expanded', isMenuOpen);

    const svg = menuToggle.querySelector('svg');
    if (isMenuOpen) {
        svg.style.transform = 'rotate(180deg)';
    } else {
        svg.style.transform = 'rotate(0deg)';
    }
});

document.addEventListener('click', function(e) {
    if (isMenuOpen && !mapControlsMenu.contains(e.target)) {
        isMenuOpen = false;
        mapControlsMenu.classList.remove('expanded');
        const svg = menuToggle.querySelector('svg');
        svg.style.transform = 'rotate(0deg)';
    }
});

// Reset to North button functionality
document.getElementById('resetNorthButton').addEventListener('click', function() {
    const currentPosition = viewer.camera.positionCartographic;
    const currentHeight = currentPosition.height;
    const currentLongitude = Cesium.Math.toDegrees(currentPosition.longitude);
    const currentLatitude = Cesium.Math.toDegrees(currentPosition.latitude);

    viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(currentLongitude, currentLatitude, currentHeight),
        orientation: {
            heading: Cesium.Math.toRadians(0.0),
            pitch: Cesium.Math.toRadians(-90),
            roll: 0.0
        },
        duration: 1.0
    });
});

// Map type toggle functionality
let isRoadMap = false;
const toggleMapTypeButton = document.getElementById('toggleMapTypeButton');
const mapTypeLabel = document.getElementById('mapTypeLabel');

toggleMapTypeButton.addEventListener('click', async function() {
    isRoadMap = !isRoadMap;

    if (isRoadMap) {
        viewer.imageryLayers.removeAll();
        viewer.imageryLayers.addImageryProvider(
            new Cesium.OpenStreetMapImageryProvider({
                url: 'https://tile.openstreetmap.org/'
            })
        );
        mapTypeLabel.textContent = 'Road Map';
    } else {
        viewer.imageryLayers.removeAll();
        const imageryProvider = await Cesium.createWorldImageryAsync();
        viewer.imageryLayers.addImageryProvider(imageryProvider);
        mapTypeLabel.textContent = 'Satellite';
    }
});

// Submit button functionality
document.getElementById('submitButton').addEventListener('click', function() {
    if (!currentPoint) {
        alert('Please place a pin on the map before submitting!');
        return;
    }

    const cartographic = Cesium.Cartographic.fromCartesian(currentPoint.position.getValue());
    const longitude = Cesium.Math.toDegrees(cartographic.longitude);
    const latitude = Cesium.Math.toDegrees(cartographic.latitude);

    const submitButton = document.getElementById('submitButton');
    submitButton.disabled = true;
    submitButton.textContent = 'SUBMITTING...';

    fetch('/api/submit-level', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            level: LEVEL,
            guess_lat: latitude,
            guess_lon: longitude
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = `/daily/level/${LEVEL}/results`;
        } else {
            alert('Error submitting guess. Please try again.');
            submitButton.disabled = false;
            submitButton.textContent = 'SUBMIT';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error submitting guess. Please try again.');
        submitButton.disabled = false;
        submitButton.textContent = 'SUBMIT';
    });
});