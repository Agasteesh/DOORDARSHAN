// This file can be used for any global JavaScript functionality.
// For the video player specific logic, it's placed directly in content_detail.html
// to ensure it loads after the video player element is present.

console.log("main.js loaded.");

document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-main.nav-links');
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
});

// --- Loader/Spinner Helper ---
function showLoader(targetSelector) {
    const target = document.querySelector(targetSelector);
    if (target) {
        const loader = document.createElement('div');
        loader.className = 'loader';
        loader.setAttribute('id', 'global-loader');
        target.appendChild(loader);
    }
}
function hideLoader() {
    const loader = document.getElementById('global-loader');
    if (loader) loader.remove();
}
// Turborepo-style navbar mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
  var hamburger = document.querySelector('.navbar-hamburger');
  if (hamburger) {
    hamburger.addEventListener('click', function(e) {
      document.body.classList.toggle('nav-open');
      e.stopPropagation();
    });
    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
      if (document.body.classList.contains('nav-open') && !e.target.closest('.glass-navbar')) {
        document.body.classList.remove('nav-open');
      }
    });
  }
});