document.addEventListener("DOMContentLoaded", function () {
  // Add active class to current page in navigation
  const currentPage = window.location.pathname.split("/").pop();
  const navLinks = document.querySelectorAll(".nav-link");

  navLinks.forEach((link) => {
    const linkHref = link.getAttribute("href").split("/").pop();
    if (
      currentPage === linkHref ||
      (currentPage === "" && linkHref === "index.html")
    ) {
      link.classList.add("active");
    }
  });

  // Animate characters on homepage
  const characters = document.querySelectorAll(".character-card");
  if (characters.length > 0) {
    characters.forEach((character, index) => {
      setTimeout(() => {
        character.style.opacity = "1";
        character.style.transform = "translateY(0)";
      }, 200 * index);
    });
  }

  // Animate title with shadow effect
  const gameTitle = document.querySelector(".game-title");
  if (gameTitle) {
    window.addEventListener("mousemove", (e) => {
      const x = e.clientX / window.innerWidth - 0.5;
      const y = e.clientY / window.innerHeight - 0.5;

      gameTitle.style.textShadow = `
                ${3 + x * 5}px ${3 + y * 5}px 0 #000, 
                ${-1 + x * 2}px ${-1 + y * 2}px 0 #000, 
                ${1 + x * 2}px ${-1 + y * 2}px 0 #000, 
                ${-1 + x * 2}px ${1 + y * 2}px 0 #000
            `;
    });
  }

  // Parallax effect for background elements
  const bgElements = document.querySelectorAll(".parallax");
  if (bgElements.length > 0) {
    window.addEventListener("scroll", () => {
      const scrollY = window.scrollY;

      bgElements.forEach((element) => {
        const speed = element.dataset.speed || 0.5;
        element.style.transform = `translateY(${scrollY * speed}px)`;
      });
    });
  }
});

// Preload character sprite animations
function preloadCharacterSprites() {
  const characters = ["Knight", "Archer", "Assassin", "Mage"];
  characters.forEach((character) => {
    const img = new Image();
    img.src = `assets/Characters/${character}/preview.gif`;
  });
}

// Call preload function after page load
window.addEventListener("load", preloadCharacterSprites);
