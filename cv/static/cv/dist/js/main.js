/**
 * main.js — vanilla ES6, no build step, no frameworks
 * Loaded via <script defer src="..."> on both page templates.
 * Each feature is a self-contained function with an early return
 * guard, so the file is safe on pages that lack those elements.
 */


/* ============================================================
   1. SCROLL-TRACKING SUBNAV
   Uses IntersectionObserver to highlight the subnav anchor that
   corresponds to whichever page section is currently mid-screen.
   Only runs on pages that have a .subnav / .site-subnav element.
   ============================================================ */

function initScrollNav() {
  // Support both the template class (.subnav) and the spec class (.site-subnav)
  const subnav = document.querySelector('.subnav, .site-subnav');
  if (!subnav) return;

  const ACTIVE = 'subnav__link--active';

  // All anchor links inside the subnav that point at on-page sections
  const links = Array.from(subnav.querySelectorAll('a[href^="#"]'));
  if (!links.length) return;

  // Resolve each href to an actual DOM section element
  const sections = links
    .map(a => document.getElementById(a.getAttribute('href').slice(1)))
    .filter(Boolean);

  function setActive(sectionId) {
    links.forEach(link => {
      link.classList.toggle(ACTIVE, link.getAttribute('href') === `#${sectionId}`);
    });
  }

  // Seed the first link as active before any scrolling occurs
  if (sections.length) setActive(sections[0].id);

  // rootMargin creates a narrow trigger band ~mid-screen:
  //   -40% from top, -55% from bottom → 5% window near the vertical centre
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        setActive(entry.target.id);
      }
    });
  }, {
    rootMargin: '-40% 0px -55% 0px',
    threshold: 0,
  });

  sections.forEach(s => observer.observe(s));
}


/* ============================================================
   2. GANTT TOOLTIPS
   A single shared tooltip element is appended to <body> and
   repositioned on each trigger.  Supports mouseenter/mouseleave
   on desktop and touchstart toggle on touch devices.

   Required data attributes on .gantt-dot:
     data-title, data-venue, data-year
     data-pdf, data-doi, data-url  (each optional — omitted when absent)
   ============================================================ */

function initGanttTooltips() {
  const dots = document.querySelectorAll('.gantt-dot');
  if (!dots.length) return;

  // --- Build the shared tooltip element -----------------------------------
  const tooltip = document.createElement('div');
  tooltip.className = 'gantt-tooltip';
  tooltip.style.position = 'fixed';
  tooltip.style.bottom = 'auto';    // prevent CSS bottom from conflicting with JS top
  tooltip.style.transform = 'none'; // prevent CSS transform from offsetting JS left
  document.body.appendChild(tooltip);

  // Delay-based hide: gives the cursor time to travel from a dot onto the
  // tooltip so the user can read it and click the links inside it.
  let hideTimer = null;

  function cancelHide() {
    if (hideTimer !== null) {
      clearTimeout(hideTimer);
      hideTimer = null;
    }
  }

  function scheduleHide() {
    cancelHide();
    hideTimer = setTimeout(hide, 200);
  }

  function renderContent(dot) {
    let pubs;
    try { pubs = JSON.parse(dot.dataset.pubs); } catch (e) { return; }
    if (!pubs || !pubs.length) return;

    function buildLinks(p) {
      let html = '';
      if (p.project) html += `<a href="${p.project}" target="_blank" rel="noopener noreferrer"
          style="color:inherit;margin-right:8px;text-decoration:underline;font-size:1.0rem">Project</a>`;
      if (p.doi) html += `<a href="https://doi.org/${p.doi}" target="_blank" rel="noopener noreferrer"
          style="color:inherit;margin-right:8px;text-decoration:underline;font-size:1.0rem">DOI</a>`;
      if (p.url) html += `<a href="${p.url}" target="_blank" rel="noopener noreferrer"
          style="color:inherit;text-decoration:underline;font-size:1.0rem">Link</a>`;
      return html;
    }

    tooltip.innerHTML = pubs.map((p, i) => {
      const meta      = [p.venue, p.year].filter(Boolean).join(' · ');
      const linksHtml = buildLinks(p);
      const badges    = (p.otherThemes || []).map(t =>
        `<span style="display:inline-block;font-size:0.85rem;padding:1px 6px;border-radius:3px;` +
        `background:var(--color-theme-${t.color});color:#fff;margin-right:4px;opacity:0.9">${t.title}</span>`
      ).join('');
      const divider = i > 0
        ? '<div style="border-top:1px solid rgba(255,255,255,0.2);margin:7px 0"></div>'
        : '';
      return `${divider}
        <strong style="display:block;line-height:1.4;margin-bottom:3px">${p.title}</strong>
        ${badges    ? `<span style="display:block;margin-bottom:4px">${badges}</span>` : ''}
        ${meta      ? `<span style="display:block;opacity:0.8;margin-bottom:${linksHtml ? '6px' : '0'}">${meta}</span>` : ''}
        ${linksHtml ? `<span style="display:block">${linksHtml}</span>` : ''}`;
    }).join('');
  }

  function show(dot) {
    cancelHide();
    renderContent(dot);

    const dotRect = dot.getBoundingClientRect();
    const ttW = tooltip.offsetWidth || 220;
    const ttH = tooltip.offsetHeight;
    const OFFSET_Y = 12;

    let left = dotRect.left + dotRect.width / 2 - ttW / 2;
    let top  = dotRect.bottom + OFFSET_Y;

    // Clamp horizontal so the tooltip doesn't overflow the viewport edges
    left = Math.max(8, Math.min(left, window.innerWidth - ttW - 8));
    // If the tooltip overflows the bottom, flip it above the dot instead
    if (top + ttH > window.innerHeight - 8) {
      top = dotRect.top - ttH - OFFSET_Y;
    }

    tooltip.style.left = `${left}px`;
    tooltip.style.top  = `${top}px`;
    tooltip.classList.add('gantt-tooltip--visible');
    tooltip._activeDot = dot;
  }

  function hide() {
    hideTimer = null;
    tooltip.classList.remove('gantt-tooltip--visible');
    tooltip._activeDot = null;
  }

  // Keep the tooltip alive while the cursor is over it so links are clickable
  tooltip.addEventListener('mouseenter', cancelHide);
  tooltip.addEventListener('mouseleave', scheduleHide);

  // --- Wire up each dot ---------------------------------------------------
  let isTouchDevice = false;

  dots.forEach(dot => {
    // Desktop hover
    dot.addEventListener('mouseenter', () => {
      if (!isTouchDevice) show(dot);
    });
    dot.addEventListener('mouseleave', () => {
      if (!isTouchDevice) scheduleHide();
    });
    // Keyboard focus (screen readers / tab navigation)
    dot.addEventListener('focus', () => show(dot));
    dot.addEventListener('blur',  hide);

    // Touch: toggle on tap
    dot.addEventListener('touchstart', e => {
      isTouchDevice = true;
      e.preventDefault(); // suppress subsequent mouseenter
      if (tooltip.classList.contains('gantt-tooltip--visible') &&
          tooltip._activeDot === dot) {
        hide();
      } else {
        show(dot);
      }
    }, { passive: false });
  });

  // Dismiss tooltip when tapping outside a dot or the tooltip itself
  document.addEventListener('touchstart', e => {
    if (isTouchDevice &&
        !e.target.classList.contains('gantt-dot') &&
        !tooltip.contains(e.target)) {
      hide();
    }
  });
}


/* ============================================================
   3. CITE MODAL
   Clicking a .pub-link--cite button opens a modal with two tabs:
   a formatted (APA-style) citation and the raw BibTeX entry.
   A Copy button writes the visible tab's text to the clipboard.
   Data is read from data-bibtex and data-pub on the parent .pub-item.
   ============================================================ */

function initCiteButtons() {
  const buttons = document.querySelectorAll('.pub-link--cite');
  if (!buttons.length) return;

  // --- Build the shared modal element ------------------------------------
  const overlay = document.createElement('div');
  overlay.className = 'cite-modal-overlay';
  overlay.setAttribute('role', 'dialog');
  overlay.setAttribute('aria-modal', 'true');
  overlay.setAttribute('aria-label', 'Citation');
  overlay.innerHTML = `
    <div class="cite-modal">
      <div class="cite-modal__header">
        <div class="cite-modal__tabs" role="tablist">
          <button class="cite-modal__tab cite-modal__tab--active" role="tab"
                  aria-selected="true" data-tab="formatted">Formatted (APA)</button>
          <button class="cite-modal__tab" role="tab"
                  aria-selected="false" data-tab="bibtex">BibTeX</button>
        </div>
        <button class="cite-modal__close" aria-label="Close">&times;</button>
      </div>
      <div class="cite-modal__body">
        <pre class="cite-modal__pre"></pre>
        <button class="cite-modal__copy" type="button">Copy</button>
      </div>
    </div>`;
  document.body.appendChild(overlay);

  const tabs    = overlay.querySelectorAll('.cite-modal__tab');
  const pre     = overlay.querySelector('.cite-modal__pre');
  const copyBtn = overlay.querySelector('.cite-modal__copy');
  const closeBtn = overlay.querySelector('.cite-modal__close');

  let bibtexText    = '';
  let formattedText = '';

  // --- Formatted (APA-ish) citation builder ------------------------------
  function buildFormatted(pub) {
    const authors = (pub.authors || []).map(a => {
      const initial = a.first ? a.first[0] + '.' : '';
      return initial ? `${a.last}, ${initial}` : a.last;
    });
    let authorStr;
    if (authors.length <= 1) {
      authorStr = authors[0] || '';
    } else {
      authorStr = authors.slice(0, -1).join(', ') + ' & ' + authors[authors.length - 1];
    }
    let cite = `${authorStr} (${pub.year}). ${pub.title}. ${pub.venue}.`;
    if (pub.doi) cite += ` https://doi.org/${pub.doi}`;
    return cite;
  }

  // --- Tab switching -----------------------------------------------------
  function showTab(tabName) {
    tabs.forEach(t => {
      const active = t.dataset.tab === tabName;
      t.classList.toggle('cite-modal__tab--active', active);
      t.setAttribute('aria-selected', active ? 'true' : 'false');
    });
    pre.textContent = tabName === 'bibtex' ? bibtexText : formattedText;
    copyBtn.textContent = 'Copy';
  }

  // --- Open / close ------------------------------------------------------
  function show(btn) {
    const li = btn.closest('.pub-item');
    try { bibtexText = JSON.parse(li.dataset.bibtex || '""'); } catch (e) { bibtexText = ''; }
    try { formattedText = buildFormatted(JSON.parse(li.dataset.pub || '{}')); } catch (e) { formattedText = ''; }
    showTab('formatted');
    overlay.classList.add('cite-modal-overlay--visible');
    closeBtn.focus();
  }

  function hide() {
    overlay.classList.remove('cite-modal-overlay--visible');
  }

  // --- Copy to clipboard -------------------------------------------------
  copyBtn.addEventListener('click', () => {
    const text = pre.textContent;
    const done = () => {
      copyBtn.textContent = 'Copied!';
      setTimeout(() => { copyBtn.textContent = 'Copy'; }, 2000);
    };
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(done).catch(() => fallbackCopy(text, done));
    } else {
      fallbackCopy(text, done);
    }
  });

  function fallbackCopy(text, cb) {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.cssText = 'position:fixed;opacity:0;top:0;left:0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); cb(); } catch (_) {}
    document.body.removeChild(ta);
  }

  // --- Event wiring -------------------------------------------------------
  tabs.forEach(tab => tab.addEventListener('click', () => showTab(tab.dataset.tab)));
  closeBtn.addEventListener('click', hide);
  overlay.addEventListener('click', e => { if (e.target === overlay) hide(); });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && overlay.classList.contains('cite-modal-overlay--visible')) hide();
  });
  buttons.forEach(btn => btn.addEventListener('click', () => show(btn)));
}


/* ============================================================
   4. PUBLICATION THEME FILTER
   Clicking a .pub-filter__btn filters .pub-item elements by
   the theme slug stored in their data-themes attribute.
   Also handles an on-load ?filter=<slug> URL parameter so that
   project card "N publications" links can deep-link into a
   pre-filtered publication list.
   Only runs if .pub-filter exists on the page.
   ============================================================ */

function initPubFilter() {
  const filterBar = document.querySelector('.pub-filter');
  if (!filterBar) return;

  const buttons = filterBar.querySelectorAll('.pub-filter__btn');
  const items   = document.querySelectorAll('.pub-item');
  if (!buttons.length || !items.length) return;

  const ACTIVE_BTN = 'pub-filter__btn--active';
  const HIDDEN_ITEM = 'pub-item--hidden';

  function applyFilter(theme) {
    // Update button active state
    buttons.forEach(btn => {
      btn.classList.toggle(ACTIVE_BTN, btn.dataset.theme === theme);
      btn.setAttribute('aria-pressed', btn.dataset.theme === theme ? 'true' : 'false');
    });

    // Show/hide publication items
    items.forEach(item => {
      if (theme === 'all') {
        item.classList.remove(HIDDEN_ITEM);
      } else {
        // data-themes is a space-separated list of theme slugs
        const themes = (item.dataset.themes || '').split(' ');
        item.classList.toggle(HIDDEN_ITEM, !themes.includes(theme));
      }
    });
  }

  // Wire up filter buttons
  buttons.forEach(btn => {
    btn.addEventListener('click', () => applyFilter(btn.dataset.theme));
  });

  // Check for ?filter= URL parameter on page load
  const params = new URLSearchParams(window.location.search);
  const urlFilter = params.get('filter');
  if (urlFilter) {
    // Find a button that matches the requested slug
    const matchBtn = Array.from(buttons).find(b => b.dataset.theme === urlFilter);
    if (matchBtn) {
      applyFilter(urlFilter);
    } else {
      // No matching theme button — apply as a freeform filter against data-themes
      // (supports project-slug filtering once pub-items gain a data-projects attribute)
      items.forEach(item => {
        const themes = (item.dataset.themes || '').split(' ');
        item.classList.toggle(HIDDEN_ITEM, !themes.includes(urlFilter));
      });
    }
    // Scroll to the publications section
    const pubSection = document.getElementById('publications');
    if (pubSection) {
      // Small delay so the browser has finished initial layout
      requestAnimationFrame(() => pubSection.scrollIntoView({ behavior: 'smooth' }));
    }
  }
}


/* ============================================================
   5. PROJECT DEPLOYMENTS EXPAND / COLLAPSE
   Each platform card has a ".deployments-preview__pill--overflow"
   button ("+N more") linked via aria-controls to a hidden
   .deployments-expanded grid.  Clicking the pill reveals the grid
   and updates the button text.  Only runs if overflow pills exist.
   ============================================================ */

function initDeployments() {
  // Support both the template class and the spec class
  const overflowPills = document.querySelectorAll(
    '.deployments-preview__pill--overflow, .deployment-pill--overflow'
  );
  if (!overflowPills.length) return;

  overflowPills.forEach(pill => {
    const targetId = pill.getAttribute('aria-controls');
    if (!targetId) return;

    const grid = document.getElementById(targetId);
    if (!grid) return;

    // Store the original "+N more" text so we can restore it on collapse
    const originalText = pill.textContent.trim();

    pill.addEventListener('click', () => {
      const isCurrentlyExpanded = !grid.hidden;

      if (isCurrentlyExpanded) {
        grid.hidden = true;
        pill.setAttribute('aria-expanded', 'false');
        pill.textContent = originalText;
      } else {
        grid.hidden = false;
        pill.setAttribute('aria-expanded', 'true');
        pill.textContent = 'show less';
      }
    });
  });
}


/* ============================================================
   BOOTSTRAP
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  initScrollNav();
  initGanttTooltips();
  initCiteButtons();
  initPubFilter();
  initDeployments();
});
