<template>
  <svg width="300" height="100" viewBox="0 0 300 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <!-- Hand-drawn style ellipse -->
    <path 
      d="M20,50 
         C20,10 280,10 280,50 
         C280,90 20,90 20,50 
         M20,50 
         C20,45 30,50 35,50" 
      stroke="#D71920" 
      stroke-width="3" 
      stroke-linecap="round" 
      class="draw-path"
    />
  </svg>
  <style>
    .draw-path {
      stroke-dasharray: 1000;
      stroke-dashoffset: 1000;
      animation: draw 1.5s ease-out forwards;
    }
    @keyframes draw {
      to {
        stroke-dashoffset: 0;
      }
    }
  </style>
</template>
