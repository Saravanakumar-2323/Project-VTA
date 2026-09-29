document.addEventListener('DOMContentLoaded', () => {
   let body = document.body;
   let sideBar = document.querySelector('.side-bar');
   let profile = document.querySelector('.header .flex .profile');
   let menuBtn = document.querySelector('#menu-btn');
   let userBtn = document.querySelector('#user-btn');
   let closeBtn = document.querySelector('#close-btn');
   let toggleBtn = document.querySelector('#toggle-btn');

   // Dark Mode Logic
   let darkMode = localStorage.getItem('dark-mode');

   const enableDarkMode = () => {
      if (toggleBtn) toggleBtn.classList.replace('fa-sun', 'fa-moon');
      body.classList.add('dark');
      localStorage.setItem('dark-mode', 'enabled');
   }

   const disableDarkMode = () => {
      if (toggleBtn) toggleBtn.classList.replace('fa-moon', 'fa-sun');
      body.classList.remove('dark');
      localStorage.setItem('dark-mode', 'disabled');
   }

   if (darkMode === 'enabled') enableDarkMode();

   if (toggleBtn) {
      toggleBtn.onclick = () => {
         darkMode = localStorage.getItem('dark-mode');
         if (darkMode === 'disabled' || !darkMode) {
            enableDarkMode();
         } else {
            disableDarkMode();
         }
      }
   }

   // 1. Hamburger Click Toggle
   if (menuBtn) {
      menuBtn.onclick = (e) => {
         e.stopPropagation();
         if (sideBar) sideBar.classList.toggle('active');
         if (profile) profile.classList.remove('active');
      };
   }

   // 2. User Button Click Toggle (Profile Popup)
   if (userBtn) {
      userBtn.onclick = (e) => {
         e.stopPropagation();
         if (profile) profile.classList.toggle('active');
         if (sideBar) sideBar.classList.remove('active');
      };
   }

   // Close Sidebar Icon Click
   if (closeBtn) {
      closeBtn.onclick = () => {
         if (sideBar) sideBar.classList.remove('active');
      };
   }

   // Auto Close on Window Scroll or Outside Click
   window.onscroll = () => {
      if (profile) profile.classList.remove('active');
      if (sideBar) sideBar.classList.remove('active');
   };

   document.onclick = (e) => {
      if (sideBar && !sideBar.contains(e.target) && e.target !== menuBtn) {
         sideBar.classList.remove('active');
      }
      if (profile && !profile.contains(e.target) && e.target !== userBtn) {
         profile.classList.remove('active');
      }
   };
});