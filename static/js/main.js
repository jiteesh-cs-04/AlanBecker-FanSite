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

// 2. The stickman's head follows your mouse
const head = document.getElementById("head");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (head && !reduceMotion) {
  document.addEventListener("mousemove", (e) => {
    const x = (e.clientX / window.innerWidth - 0.5) * 14;
    const y = (e.clientY / window.innerHeight - 0.5) * 10;
    head.style.transform = `translate(${x}px, ${y}px)`;
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