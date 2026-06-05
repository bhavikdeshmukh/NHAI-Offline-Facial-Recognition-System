const tabs = document.querySelectorAll(".nav-tab");
const screens = document.querySelectorAll(".screen");
const title = document.querySelector("#screen-title");
const actionButtons = document.querySelectorAll("[data-go]");

const screenTitles = {
  verify: "Offline Verification",
  enroll: "Officer Enrollment",
  liveness: "Active Liveness Check",
  result: "Verification Result",
  sync: "Pending Sync Queue",
};

function showScreen(id) {
  screens.forEach((screen) => {
    screen.classList.toggle("active", screen.id === id);
  });

  tabs.forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.step === id);
  });

  title.textContent = screenTitles[id];
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => showScreen(tab.dataset.step));
});

actionButtons.forEach((button) => {
  button.addEventListener("click", () => showScreen(button.dataset.go));
});
