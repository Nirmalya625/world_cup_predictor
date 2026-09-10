/**
 * World Cup 2026 Predictor — animation layer.
 * Pure vanilla JS, no dependencies. Handles:
 *   1. Staggered fade/rise reveal for cards + table rows (IntersectionObserver)
 *   2. Count-up animation for every [data-count] percentage
 *   3. Width animation for every [data-bar] confidence bar
 * All of it is skipped in favor of instant final states if the visitor's
 * OS has "reduce motion" turned on.
 */
(function () {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function animateCount(el, target, duration) {
    if (reduceMotion) {
      el.textContent = target.toFixed(1) + "%";
      return;
    }
    const start = performance.now();
    function tick(now) {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3); // ease-out cubic
      el.textContent = (target * eased).toFixed(1) + "%";
      if (t < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function reveal(el) {
    el.classList.add("is-visible");

    el.querySelectorAll("[data-bar]").forEach((bar) => {
      const target = parseFloat(bar.dataset.bar);
      if (reduceMotion) {
        bar.style.width = target + "%";
      } else {
        requestAnimationFrame(() => {
          bar.style.width = target + "%";
        });
      }
    });

    el.querySelectorAll("[data-count]").forEach((numEl) => {
      const target = parseFloat(numEl.dataset.count);
      animateCount(numEl, target, 1100);
    });
  }

  // Stagger: give each child of a [data-stagger] group an incremental delay
  // so groups of cards/rows reveal in sequence rather than all at once.
  document.querySelectorAll("[data-stagger]").forEach((group) => {
    Array.from(group.children).forEach((child, i) => {
      child.style.transitionDelay = reduceMotion ? "0ms" : `${i * 90}ms`;
    });
  });

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          reveal(entry.target);
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  document.querySelectorAll(".reveal:not(.is-hero)").forEach((el) => io.observe(el));

  // Hero reveals immediately on load rather than waiting for scroll.
  const hero = document.querySelector(".is-hero");
  if (hero) requestAnimationFrame(() => reveal(hero));
})();
