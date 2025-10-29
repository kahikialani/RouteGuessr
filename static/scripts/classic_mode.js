const particleContainer = document.getElementById('particleContainer');
const numParticles = 50;

function createParticle() {
    const particle = document.createElement('div');
    particle.className = 'particle';

    // Random starting position
    const startX = Math.random() * window.innerWidth;
    const startY = Math.random() * window.innerHeight;

    particle.style.left = startX + 'px';
    particle.style.top = startY + 'px';

    // Random distance to travel
    const xDistance = (Math.random() - 0.5) * 400; // -200 to 200px
    const yDistance = (Math.random() - 0.5) * 400;

    particle.style.setProperty('--x-distance', xDistance + 'px');
    particle.style.setProperty('--y-distance', yDistance + 'px');

    // Random animation duration and delay
    const duration = 8 + Math.random() * 12; // 8-20 seconds
    const delay = Math.random() * 5; // 0-5 seconds

    particle.style.animationDuration = duration + 's';
    particle.style.animationDelay = delay + 's';

    // Random size variation
    const size = 1 + Math.random() * 3; // 3-6px
    particle.style.width = size + 'px';
    particle.style.height = size + 'px';

    particleContainer.appendChild(particle);
}

// Generate particles
for (let i = 0; i < numParticles; i++) {
    createParticle();
}