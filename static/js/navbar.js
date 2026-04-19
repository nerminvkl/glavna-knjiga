function toggleNav() {
    const nav = document.getElementById('topbar-nav');
    const btn = document.querySelector('.nav-hamburger');
    nav.classList.toggle('open');
    btn.classList.toggle('open');
  }
  
  // Close nav when clicking a link on mobile
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.getElementById('topbar-nav').classList.remove('open');
      document.querySelector('.nav-hamburger').classList.remove('open');
    });
  });