// 1. Live taskbar clock
const clock = document.getElementById("clock");
function updateClock() {
  const now = new Date();
  clock.textContent = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}
if (clock) {
  updateClock();
  setInterval(updateClock, 30000);
}

const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// 2. The five stickmen lean toward your mouse
const minis = document.querySelectorAll(".mini");
if (minis.length && !reduceMotion) {
  document.addEventListener("mousemove", (e) => {
    const lean = (e.clientX / window.innerWidth - 0.5) * 14;
    minis.forEach((m, i) => m.style.setProperty("--lean", `${lean * (1 + i * 0.12)}deg`));
  });
}

// 3. The close button refuses to close
const closeBtn = document.getElementById("close-btn");
if (closeBtn) {
  closeBtn.addEventListener("click", () => {
    const win = closeBtn.closest(".window");
    win.classList.remove("shake");
    void win.offsetWidth; // restart the animation
    win.classList.add("shake");
  });
}

// 4. Live character counter on the message box
const msg = document.getElementById("message");
const counter = document.getElementById("char-count");
if (msg && counter) {
  const update = () => { counter.textContent = msg.value.length; };
  msg.addEventListener("input", update);
  update();
}

// 5. Reveal sections as you scroll down
const revealEls = document.querySelectorAll(".reveal");
if ("IntersectionObserver" in window && revealEls.length) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("in");
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });
  revealEls.forEach((el) => io.observe(el));
} else {
  revealEls.forEach((el) => el.classList.add("in"));
}