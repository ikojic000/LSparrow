/*!
 * LSparrow - Core Scripts
 * Modern Tailwind-based design
 */

window.addEventListener("DOMContentLoaded", function () {
  // ===== Dark Mode Toggle =====
  function isDark() {
    return document.documentElement.classList.contains("dark");
  }

  function updateDarkIcons() {
    var icon = isDark() ? "fa-sun" : "fa-moon";
    var remove = isDark() ? "fa-moon" : "fa-sun";
    var el = document.getElementById("darkModeIcon");
    if (el) {
      el.classList.remove(remove);
      el.classList.add(icon);
    }
  }

  function toggleDarkMode() {
    var html = document.documentElement;
    html.classList.toggle("dark");
    localStorage.setItem("ls-theme", isDark() ? "dark" : "light");
    updateDarkIcons();
  }

  // Set initial icon state
  updateDarkIcons();

  var dmToggle = document.getElementById("darkModeToggle");
  if (dmToggle) dmToggle.addEventListener("click", toggleDarkMode);

  // ===== Mobile nav toggle =====
  var navToggle = document.getElementById("navToggle");
  var mobileMenu = document.getElementById("mobileMenu");
  var navToggleIcon = document.getElementById("navToggleIcon");

  if (navToggle && mobileMenu) {
    navToggle.addEventListener("click", function () {
      mobileMenu.classList.toggle("hidden");
      if (navToggleIcon) {
        navToggleIcon.classList.toggle("fa-bars");
        navToggleIcon.classList.toggle("fa-times");
      }
    });
    // Close mobile menu on link click
    mobileMenu.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        mobileMenu.classList.add("hidden");
        if (navToggleIcon) {
          navToggleIcon.classList.add("fa-bars");
          navToggleIcon.classList.remove("fa-times");
        }
      });
    });
  }

  // ===== Navbar scroll behavior =====
  var mainNav = document.getElementById("mainNav");
  var hasHero = document.querySelector(".hero-gradient");

  function updateNav() {
    if (!mainNav) return;
    if (hasHero) {
      // Home page: transparent at top, frosted glass when scrolled
      if (window.scrollY < 50) {
        mainNav.classList.add("nav-transparent");
      } else {
        mainNav.classList.remove("nav-transparent");
      }
    }
  }

  updateNav();
  document.addEventListener("scroll", updateNav);
});
