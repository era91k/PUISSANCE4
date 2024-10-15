const confettiElement = document.getElementById('confetti');

function createConfetti() {
    confettiElement.style.display = 'block';
    for (let i = 0; i < 100; i++) {
        const confettiPiece = document.createElement('div');
        confettiPiece.classList.add('confetti-piece');
        confettiPiece.style.backgroundColor = `hsl(${Math.random() * 360}, 100%, 50%)`;
        confettiPiece.style.left = `${Math.random() * 100}%`;
        confettiPiece.style.animationDelay = `${Math.random() * 2}s`;
        confettiPiece.style.transform = `translateY(-50px) rotate(${Math.random() * 360}deg)`;
        confettiElement.appendChild(confettiPiece);

        // Enlever le confetti après animation
        setTimeout(() => {
            confettiPiece.remove();
        }, 3000);
    }
}