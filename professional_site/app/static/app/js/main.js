"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const loader = document.getElementById("siteLoader");
  const revealPage = () => {
    loader?.classList.add("is-hidden");
    document.body.classList.add("page-ready");
  };
  window.addEventListener("load", () => window.setTimeout(revealPage, reducedMotion ? 0 : 350), { once: true });
  window.setTimeout(revealPage, 2800);
  window.addEventListener("pageshow", revealPage);

  document.addEventListener("click", event => {
    const link = event.target.closest("a");
    if (!link || event.defaultPrevented || event.button > 0 || event.metaKey || event.ctrlKey ||
        event.shiftKey || event.altKey || link.classList.contains("js-content-preview") ||
        link.hasAttribute("download") || link.target === "_blank" ||
        link.dataset.bsToggle || link.href.startsWith("mailto:") || link.href.startsWith("tel:")) return;
    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin || (url.pathname === location.pathname && url.hash)) return;
    event.preventDefault();
    loader?.classList.remove("is-hidden");
    loader?.classList.add("is-navigating");
    window.setTimeout(() => { location.href = link.href; }, reducedMotion ? 0 : 180);
  });

  const header = document.querySelector(".site-header");
  const backTop = document.querySelector(".back-top");
  const progress = document.querySelector(".scroll-progress span");
  let scrollQueued = false;
  const updateScrollUI = () => {
    const y = window.scrollY;
    header?.classList.toggle("is-scrolled", y > 32);
    backTop?.classList.toggle("show", y > 500);
    const available = document.documentElement.scrollHeight - innerHeight;
    if (progress) progress.style.transform = `scaleX(${available > 0 ? Math.min(1, y / available) : 0})`;
    scrollQueued = false;
  };
  window.addEventListener("scroll", () => {
    if (!scrollQueued) { requestAnimationFrame(updateScrollUI); scrollQueued = true; }
  }, { passive: true });
  updateScrollUI();
  backTop?.addEventListener("click", () => window.scrollTo({ top: 0, behavior: reducedMotion ? "auto" : "smooth" }));

  const menu = document.getElementById("mobileNav");
  const trigger = document.querySelector(".menu-trigger");
  menu?.addEventListener("show.bs.offcanvas", () => trigger?.classList.add("is-open"));
  menu?.addEventListener("hidden.bs.offcanvas", () => trigger?.classList.remove("is-open"));
  menu?.querySelectorAll("a").forEach(link => link.addEventListener("click", () => {
    bootstrap.Offcanvas.getInstance(menu)?.hide();
  }));

  document.querySelectorAll(".two-column, .bio-grid, .contact-grid").forEach(layout => {
    const children = [...layout.children];
    children[0]?.setAttribute("data-reveal", "fade-right");
    children[1]?.setAttribute("data-reveal", "fade-left");
  });
  document.querySelectorAll(".card-grid, .gallery-grid, .skill-list, .publication-list, .footer-grid").forEach(group => {
    group.setAttribute("data-stagger", "");
    [...group.children].forEach(child => child.dataset.reveal ||= "fade-up");
  });
  document.querySelectorAll(".cta, .contact-form, .compact-record, .values-panel, .about-portrait").forEach(item => {
    item.dataset.reveal ||= item.matches("img") ? "image" : "fade-up";
  });
  document.querySelectorAll(".site-footer .footer-grid > div").forEach(item => item.dataset.reveal = "fade-up");

  const revealItems = document.querySelectorAll("[data-reveal], .reveal, .professional-card, .publication-item, .timeline article");
  document.querySelectorAll("[data-stagger]").forEach(group => {
    const step = Math.max(25, Math.min(100, Number(group.dataset.staggerStep) || 70));
    [...group.children].forEach((child, index) => {
      child.style.setProperty("--reveal-delay", `${Math.min(index * step, 420)}ms`);
    });
  });
  revealItems.forEach((item, index) => {
    item.dataset.reveal ||= "fade-up";
    item.style.setProperty("--reveal-delay", `${Math.min(index % 6, 5) * 55}ms`);
  });
  if (!reducedMotion && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add("is-visible"); observer.unobserve(entry.target); }
    }), { threshold: 0.12, rootMargin: "0px 0px -30px" });
    revealItems.forEach(item => observer.observe(item));
  } else revealItems.forEach(item => item.classList.add("is-visible"));

  document.querySelectorAll(".timeline").forEach(timeline => {
    timeline.classList.add("motion-timeline");
    const items = timeline.querySelectorAll("article");
    if (reducedMotion || !("IntersectionObserver" in window)) {
      timeline.classList.add("is-drawn");
      items.forEach(item => item.classList.add("is-timeline-visible"));
      return;
    }
    const timelineObserver = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-drawn");
      timelineObserver.unobserve(entry.target);
    }), { threshold: .08 });
    timelineObserver.observe(timeline);
    const itemObserver = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-timeline-visible");
        itemObserver.unobserve(entry.target);
      }
    }), { threshold: .25 });
    items.forEach(item => itemObserver.observe(item));
  });

  const cvLinks = [...document.querySelectorAll(".cv-index a")];
  if (cvLinks.length && "IntersectionObserver" in window) {
    const sectionObserver = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      cvLinks.forEach(link => {
        const active = link.hash === `#${entry.target.id}`;
        link.classList.toggle("is-active", active);
        if (active) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
    }), { rootMargin: "-25% 0px -60%", threshold: 0 });
    cvLinks.forEach(link => {
      const section = document.querySelector(link.hash);
      if (section) sectionObserver.observe(section);
    });
  }

  document.querySelectorAll(".metrics-grid strong").forEach(value => {
    const match = value.textContent.trim().match(/^(\d+)(.*)$/);
    if (!match) return;
    const target = Number(match[1]), suffix = match[2];
    value.dataset.counterTarget = target;
    if (reducedMotion) return;
    value.textContent = `0${suffix}`;
    const counterObserver = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const start = performance.now();
      const tick = now => {
        const amount = Math.min(1, (now - start) / 900);
        value.textContent = `${Math.round(target * (1 - Math.pow(1 - amount, 3)))}${suffix}`;
        if (amount < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
      counterObserver.disconnect();
    }), { threshold: .5 });
    counterObserver.observe(value);
  });

  const modalElement = document.getElementById("contentDetailModal");
  const modalBody = document.getElementById("contentDetailBody");
  let activeTrigger = null;
  const skeleton = `<div class="preview-skeleton" aria-label="Loading preview"><span class="skeleton-line short"></span><span class="skeleton-line title"></span><span class="skeleton-line medium"></span><span class="skeleton-media"></span><span class="skeleton-line"></span><span class="skeleton-line"></span><span class="skeleton-line medium"></span></div>`;
  document.addEventListener("click", async event => {
    const link = event.target.closest(".js-content-preview");
    if (!link || !modalElement || !window.bootstrap) return;
    event.preventDefault();
    activeTrigger = link;
    modalBody.innerHTML = skeleton;
    bootstrap.Modal.getOrCreateInstance(modalElement).show(link);
    try {
      const response = await fetch(link.dataset.previewUrl, { headers: { "X-Requested-With": "XMLHttpRequest" } });
      if (!response.ok) throw new Error("Preview unavailable");
      modalBody.innerHTML = await response.text();
      modalBody.querySelector("h2")?.focus({ preventScroll: true });
    } catch {
      modalBody.innerHTML = `<div class="preview-error"><i class="bi bi-exclamation-circle"></i><h2 id="contentDetailModalLabel">We couldn't load the preview.</h2><p>You can still open the complete page.</p><a class="btn btn-accent" href="${link.dataset.fullUrl}">Open full page</a><button class="btn btn-outline" type="button" data-bs-dismiss="modal">Close</button></div>`;
    }
  });
  modalElement?.addEventListener("hidden.bs.modal", () => activeTrigger?.focus());

  document.addEventListener("click", async event => {
    const button = event.target.closest(".js-share");
    if (!button) return;
    const label = button.querySelector("span");
    const original = label?.textContent || "Copy link";
    try {
      if (navigator.share && button.dataset.preferShare === "true") {
        await navigator.share({ title: button.dataset.shareTitle, url: button.dataset.shareUrl });
      } else if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(button.dataset.shareUrl);
      } else {
        const input = document.createElement("textarea");
        input.value = button.dataset.shareUrl; input.style.position = "fixed"; input.style.opacity = "0";
        document.body.append(input); input.select(); document.execCommand("copy"); input.remove();
      }
      if (label) label.textContent = "Copied!";
      window.setTimeout(() => { if (label) label.textContent = original; }, 1600);
    } catch { if (label) label.textContent = "Copy failed"; }
  });

  const galleryModal = document.getElementById("galleryModal");
  galleryModal?.addEventListener("show.bs.modal", event => {
    const trigger = event.relatedTarget;
    const image = galleryModal.querySelector("#galleryModalImage");
    if (image && trigger.dataset.image) { image.src = trigger.dataset.image; image.alt = trigger.dataset.alt; }
    galleryModal.querySelector("#galleryModalCaption").textContent = trigger.dataset.caption || "";
  });
  galleryModal?.addEventListener("hidden.bs.modal", () => {
    const image = galleryModal.querySelector("#galleryModalImage"); if (image) image.src = "";
  });

  const portrait = document.querySelector("[data-portrait-stage]");
  if (portrait && !reducedMotion && matchMedia("(hover:hover) and (pointer:fine)").matches) {
    portrait.addEventListener("pointermove", event => {
      const rect = portrait.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - .5;
      const y = (event.clientY - rect.top) / rect.height - .5;
      portrait.style.transform = `perspective(900px) rotateX(${-y * 2}deg) rotateY(${x * 3}deg) translate3d(${x * 3}px,${y * 3}px,0)`;
    });
    portrait.addEventListener("pointerleave", () => portrait.style.transform = "");
  }

  if (portrait && !reducedMotion) {
    const media = portrait.querySelector(".portrait-media");
    const panel = portrait.querySelector(".portrait-panel");
    const badge = portrait.querySelector(".portrait-credential-card");
    let portraitQueued = false;
    const updatePortrait = () => {
      const rect = portrait.getBoundingClientRect();
      const progress = Math.max(-1, Math.min(1, (innerHeight / 2 - (rect.top + rect.height / 2)) / innerHeight));
      media?.style.setProperty("--portrait-shift", `${progress * 12}px`);
      panel?.style.setProperty("--portrait-depth", `${progress * -9}px`);
      badge?.style.setProperty("--portrait-depth", `${progress * 7}px`);
      portraitQueued = false;
    };
    window.addEventListener("scroll", () => {
      if (!portraitQueued) { requestAnimationFrame(updatePortrait); portraitQueued = true; }
    }, { passive: true });
    updatePortrait();
  }

  document.querySelectorAll(".contact-form").forEach(form => form.addEventListener("submit", event => {
    if (!form.checkValidity()) return;
    const button = form.querySelector("[type=submit]");
    button?.classList.add("is-loading");
    if (button) button.innerHTML = `Sending… <span class="button-loader" aria-hidden="true"></span>`;
  }));
});
