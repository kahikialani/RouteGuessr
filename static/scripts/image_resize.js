function calculateImageDimensions() {
    const img = document.getElementById('dynamicImage');
    const container = document.getElementById('imageContainer');
    const loading = document.getElementById('loading');

    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    const marginH = viewportWidth * 0.025;
    const marginV = viewportHeight * 0.025;

    const containerPadding = 20;

    const maxContainerWidth = viewportWidth - (2 * marginH);
    const maxContainerHeight = viewportHeight - (2 * marginV);

    const imgAspectRatio = img.naturalWidth / img.naturalHeight;

    const maxImageWidth = maxContainerWidth - (2 * containerPadding);
    const maxImageHeight = maxContainerHeight - (2 * containerPadding);

    let imageWidth, imageHeight;

    if (maxImageWidth / maxImageHeight > imgAspectRatio) {
        imageHeight = maxImageHeight;
        imageWidth = imageHeight * imgAspectRatio;
    } else {
        imageWidth = maxImageWidth;
        imageHeight = imageWidth / imgAspectRatio;
    }

    const containerWidth = imageWidth + (2 * containerPadding);
    const containerHeight = imageHeight + (2 * containerPadding);

    const containerLeft = (viewportWidth - containerWidth) / 2;
    const containerTop = (viewportHeight - containerHeight) / 2;

    container.style.width = containerWidth + 'px';
    container.style.height = containerHeight + 'px';
    container.style.left = containerLeft + 'px';
    container.style.top = containerTop + 'px';

    loading.style.display = 'none';
    container.style.display = 'block';
}

function loadImage(imageUrl) {
    const img = document.getElementById('dynamicImage');
    const container = document.getElementById('imageContainer');
    const loading = document.getElementById('loading');

    container.style.display = 'none';

    const tempImg = new Image();

    tempImg.onload = function() {
        img.src = imageUrl;

        img.onload = function() {
            calculateImageDimensions();
        };
    };

    tempImg.onerror = function() {
        loading.textContent = 'Error loading image';
        loading.style.display = 'block';
        container.style.display = 'none';
    };

    tempImg.src = imageUrl;
}

window.addEventListener('resize', function() {
    const img = document.getElementById('dynamicImage');
    if (img.src && img.complete) {
        calculateImageDimensions();
    }
});

window.addEventListener('load', function() {
    loadImage(IMAGE_URL);
});