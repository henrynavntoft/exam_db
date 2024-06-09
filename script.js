"use strict";

async function getRandomColor() {
  const response = await fetch("https://x-colors.yurace.pro/api/random");
  const data = await response.json();
  document.querySelector("main").style.backgroundColor = data.hex;
}

getRandomColor();
