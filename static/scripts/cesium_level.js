Cesium.Ion.defaultAccessToken = CESIUM_KEY


const viewer = new Cesium.Viewer('cesiumContainer', {
    useBrowserRecommendedResolution: false,
    terrain: Cesium.Terrain.fromWorldTerrain(),
    animation: false,
    timeline: false,
    baseLayerPicker: false,
    geocoder: false,
    homeButton: false,
    navigationHelpButton: false,
    sceneModePicker: false,
    fullscreenButton: false,
    allowPicking: false,
});

viewer.camera.setView({
    destination: Cesium.Cartesian3.fromDegrees(-103, 34, 5999999),
    orientation: {
        heading: Cesium.Math.toRadians(0.0),
        pitch: Cesium.Math.toRadians(-90),
        roll: 0.0
    }
});

viewer.scene.screenSpaceCameraController._zoomFactor = 6.0;
viewer.cesiumWidget.creditContainer.style.display = 'none';

viewer.screenSpaceEventHandler.setInputAction(function(click) {
    const cartesian = viewer.scene.pickPosition(click.position);
}, Cesium.ScreenSpaceEventType.LEFT_CLICK);


// Area Pins
const joshuaTree = viewer.entities.add({
    name: "Joshua Tree NP",
    position: Cesium.Cartesian3.fromDegrees(-116.16795, 34.0122),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },
    label: {
        text: "Joshua Tree NP",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const tahquitzAndSucide = viewer.entities.add({
    name: "tahquitzAndSuicide",
    position: Cesium.Cartesian3.fromDegrees(-116.679, 33.7607),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(100000, 20000000.0),
    },
    label: {
        text: "Tahquitz & Sucide",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(100000, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const tahquitz = viewer.entities.add({
    name: "tahquitz",
    position: Cesium.Cartesian3.fromDegrees(-116.68322, 33.76025),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 100000),
    },
    label: {
        text: "Tahquitz Rock",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 100000),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const suicideRock = viewer.entities.add({
    name: "sucideRock",
    position: Cesium.Cartesian3.fromDegrees(-116.69407, 33.77004),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 100000),
    },
    label: {
        text: "Suicide Rock",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 100000),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const yosemiteValley = viewer.entities.add({
    name: "Yosemite Valley",
    position: Cesium.Cartesian3.fromDegrees(-119.63452, 37.72349),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Yosemite Valley",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const squamish = viewer.entities.add({
    name: "Squamish",
    position: Cesium.Cartesian3.fromDegrees(-123.15393, 49.67997),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Squamish",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const indianCreek = viewer.entities.add({
    name: "Indian Creek",
    position: Cesium.Cartesian3.fromDegrees(-109.53987, 38.02574),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Indian Creek",
        font: "16pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const redRocks = viewer.entities.add({
    name: "Red Rocks",
    position: Cesium.Cartesian3.fromDegrees(-115.42451, 36.13128),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Red Rocks",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const smithRock = viewer.entities.add({
    name: "Smith Rock",
    position: Cesium.Cartesian3.fromDegrees(-121.13906, 44.36779),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Smith Rock",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const tuoloumne = viewer.entities.add({
    name: "Tuolumne Meadows",
    position: Cesium.Cartesian3.fromDegrees(-119.35782, 37.87401),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0)
    },
    label: {
        text: "Tuolumne Meadows",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const vedawoo = viewer.entities.add({
    name: "Vedauwoo",
    position: Cesium.Cartesian3.fromDegrees(-105.37821 , 41.18479),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Vedauwoo",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },
});

const tensleep = viewer.entities.add({
    name: "Ten Sleep Canyon",
    position: Cesium.Cartesian3.fromDegrees(-107.24497 , 44.13869),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Ten Sleep Canyon",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const devilsTower = viewer.entities.add({
    name: "Devils Tower",
    position: Cesium.Cartesian3.fromDegrees(-104.71507, 44.59048),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Devils Tower",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const redRiverGorge = viewer.entities.add({
    name: "Red River Gorge",
    position: Cesium.Cartesian3.fromDegrees(-83.68217, 37.67745),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Red River Gorge",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const newRiverGorge = viewer.entities.add({
    name: "New River Gorge",
    position: Cesium.Cartesian3.fromDegrees(-81.06337 , 38.07788),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "New River Gorge",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const rumney = viewer.entities.add({
    name: "Rumney",
    position: Cesium.Cartesian3.fromDegrees(-71.8367, 43.8021),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Rumney",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const theGunks = viewer.entities.add({
    name: "Shawangunks",
    position: Cesium.Cartesian3.fromDegrees(-74.20173, 41.65146),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Shawangunks",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const theNeedles = viewer.entities.add({
    name: "The Needles",
    position: Cesium.Cartesian3.fromDegrees(-118.50838, 36.11985),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "The Needles",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const bishopArea = viewer.entities.add({
    name: "Bishop",
    position: Cesium.Cartesian3.fromDegrees(-118.39539, 37.36119),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Bishop",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const loversLeap = viewer.entities.add({
    name: "Lover's Leap",
    position: Cesium.Cartesian3.fromDegrees(-120.14053, 38.79949),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Lover's Leap",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const indexWA = viewer.entities.add({
    name: "Index",
    position: Cesium.Cartesian3.fromDegrees(-121.56191, 47.82481),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Index",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const eldorado = viewer.entities.add({
    name: "Eldorado Canyon",
    position: Cesium.Cartesian3.fromDegrees(-105.28121, 39.9318),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Eldorado Canyon",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const wasatch = viewer.entities.add({
    name: "Wasatch Range",
    position: Cesium.Cartesian3.fromDegrees(-111.72869 , 40.60538),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Wasatch Range",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(50000, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const littleCW = viewer.entities.add({
    name: "Little Cottonwood",
    position: Cesium.Cartesian3.fromDegrees(-111.77699, 40.5727),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 50000.0)
    },
    label: {
        text: "Little Cottonwood Canyon",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 50000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const bigCW = viewer.entities.add({
    name: "Big Cottonwood",
    position: Cesium.Cartesian3.fromDegrees(-111.789, 40.6193),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 50000.0)
    },
    label: {
        text: "Big Cottonwood Canyon",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 50000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const cityOfRocks = viewer.entities.add({
    name: "City of Rocks",
    position: Cesium.Cartesian3.fromDegrees(-113.72398 , 39.9318),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "City of Rocks",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },

});

const rifle = viewer.entities.add({
    name: "Rifle",
    position: Cesium.Cartesian3.fromDegrees(-107.6912, 39.7159),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Rifle",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },
});
const stGeorge = viewer.entities.add({
    name: "Saint George",
    position: Cesium.Cartesian3.fromDegrees(-113.59297, 37.05079),
    point: {
        pixelSize: 5,
        color: Cesium.Color.BLACK,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
    },
    label: {
        text: "Saint George",
        font: "14pt monospace",
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineColor: Cesium.Color.GRAY,
        fillColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0.0, 2000000.0),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    },
});



// Variable to store the current point
let currentPoint = null;

function createPoint(worldPosition) {
    // Remove the previous point if it exists
    if (currentPoint) {
        viewer.entities.remove(currentPoint);
    }

    // Create new point
    currentPoint = viewer.entities.add({
        position: worldPosition,
        billboard: {
            image: PIN_ICON,
            width: 32,  // Set desired display width
            height: 48, // Set desired display height
            pixelOffset: new Cesium.Cartesian2(0, -15),
            scale: 0.65,
            heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
        },
    });

    // Show submit button
    const submitContainer = document.getElementById('submitContainer');
    if (submitContainer) {
        submitContainer.classList.add('visible');
    }

    return currentPoint;
}

const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

handler.setInputAction(function (click) {
    // Get ray from camera through click position
    const ray = viewer.camera.getPickRay(click.position);

    // Get intersection with globe
    const cartesian = viewer.scene.globe.pick(ray, viewer.scene);

    if (cartesian) {
        createPoint(cartesian);

        // Optional: Log coordinates for debugging
        const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
        const longitude = Cesium.Math.toDegrees(cartographic.longitude);
        const latitude = Cesium.Math.toDegrees(cartographic.latitude);
        console.log(`Clicked at: Lon ${longitude.toFixed(4)}, Lat ${latitude.toFixed(4)}`);
    }
}, Cesium.ScreenSpaceEventType.LEFT_CLICK);

// Reset to North button functionality
document.getElementById('resetNorthButton').addEventListener('click', function() {
    // Get current camera position
    const currentPosition = viewer.camera.positionCartographic;
    const currentHeight = currentPosition.height;
    const currentLongitude = Cesium.Math.toDegrees(currentPosition.longitude);
    const currentLatitude = Cesium.Math.toDegrees(currentPosition.latitude);

    // Smoothly fly to same position but facing north (heading = 0)
    viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(currentLongitude, currentLatitude, currentHeight),
        orientation: {
            heading: Cesium.Math.toRadians(0.0),
            pitch: Cesium.Math.toRadians(-90),
            roll: 0.0
        },
        duration: 1.0 // 1 second animation
    });
});

// Submit button functionality
document.getElementById('submitButton').addEventListener('click', function() {
    if (!currentPoint) {
        alert('Please place a pin on the map before submitting!');
        return;
    }

    // Get coordinates from the current point
    const cartographic = Cesium.Cartographic.fromCartesian(currentPoint.position.getValue());
    const longitude = Cesium.Math.toDegrees(cartographic.longitude);
    const latitude = Cesium.Math.toDegrees(cartographic.latitude);

    // Disable the submit button to prevent double submission
    const submitButton = document.getElementById('submitButton');
    submitButton.disabled = true;
    submitButton.textContent = 'Submitting...';

    // Send coordinates to the server
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
            // Redirect to results page
            window.location.href = `/daily/level/${LEVEL}/results`;
        } else {
            alert('Error submitting guess. Please try again.');
            submitButton.disabled = false;
            submitButton.textContent = 'Submit';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error submitting guess. Please try again.');
        submitButton.disabled = false;
        submitButton.textContent = 'Submit';
    });
});