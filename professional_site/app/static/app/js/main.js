"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const backTop = document.querySelector(".back-top");
  if (backTop) {
    const update = () => backTop.classList.toggle("show", window.scrollY > 500);
    update();
    window.addEventListener("scroll", update, { passive: true });
    backTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  }

  const galleryModal = document.getElementById("galleryModal");
  if (galleryModal) {
    galleryModal.addEventListener("show.bs.modal", event => {
      const trigger = event.relatedTarget;
      const image = galleryModal.querySelector("#galleryModalImage");
      image.src = trigger.dataset.image;
      image.alt = trigger.dataset.alt;
      galleryModal.querySelector("#galleryModalCaption").textContent = trigger.dataset.caption || "";
    });
    galleryModal.addEventListener("hidden.bs.modal", () => {
      galleryModal.querySelector("#galleryModalImage").src = "";
    });
  }
});
