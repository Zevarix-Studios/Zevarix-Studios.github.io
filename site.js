(() => {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const items = [...document.querySelectorAll('.reveal')];

  if (items.length) {
    if (reducedMotion.matches || !('IntersectionObserver' in window)) {
      items.forEach((item) => item.classList.add('is-visible'));
    } else {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        });
      }, {
        rootMargin: '0px 0px -8% 0px',
        threshold: 0.12,
      });

      items.forEach((item) => observer.observe(item));
    }
  }

  const easterEggStyles = document.createElement('link');
  easterEggStyles.rel = 'stylesheet';
  easterEggStyles.href = 'site-easter-egg.css';
  document.head.append(easterEggStyles);

  const hologram = document.createElement('div');
  hologram.className = 'konami-hologram';
  hologram.setAttribute('aria-hidden', 'true');
  hologram.hidden = true;

  const projection = document.createElement('div');
  projection.className = 'hologram__projection';

  const figure = document.createElement('div');
  figure.className = 'hologram__dancer';

  [
    'hologram__head',
    'hologram__torso',
    'hologram__hips',
    'hologram__arm hologram__arm--left',
    'hologram__arm hologram__arm--right',
    'hologram__leg hologram__leg--left',
    'hologram__leg hologram__leg--right',
  ].forEach((className) => {
    const part = document.createElement('span');
    part.className = className;
    figure.append(part);
  });

  const base = document.createElement('div');
  base.className = 'hologram__base';

  projection.append(figure);
  hologram.append(projection, base);
  document.body.append(hologram);

  const sequence = [
    'ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown',
    'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight',
    'b', 'a',
  ];

  let sequenceIndex = 0;
  let unlocked = false;

  window.addEventListener('keyup', (event) => {
    if (unlocked) return;

    const target = event.target;
    if (
      target instanceof HTMLElement
      && (target.matches('input, textarea, select') || target.isContentEditable)
    ) {
      sequenceIndex = 0;
      return;
    }

    const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;

    if (key === sequence[sequenceIndex]) {
      sequenceIndex += 1;

      if (sequenceIndex === sequence.length) {
        unlocked = true;
        hologram.hidden = false;
        requestAnimationFrame(() => hologram.classList.add('is-active'));
      }

      return;
    }

    sequenceIndex = key === sequence[0] ? 1 : 0;
  });
})();
