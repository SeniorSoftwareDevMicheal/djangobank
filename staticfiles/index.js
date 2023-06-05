const burger = document.querySelector(".header__burger");
const header = document.querySelector(".header");
const overlay = document.querySelector('.overlay');
const menu = document.querySelector(".burger-menu");
const menuLink = menu.childNodes;

const burgerClick = () => {
  header.classList.toggle("menu-clicked");
    if (!overlay.classList.contains('fade-in')) {
      overlay.classList.add('fade-in')
      overlay.classList.remove('fade-out')
      menu.classList.add('fade-in')
      menu.classList.remove('fade-out')
    } else {
      overlay.classList.add('fade-out')
      overlay.classList.remove('fade-in')
      menu.classList.add('fade-out')
      menu.classList.remove('fade-in')
    }
}

const menuClick = () => {
  if (header.classList.contains('menu-clicked')) {
    burgerClick()
  }
}

burger.addEventListener("click",() => burgerClick(), false);

menuLink.forEach(link => {
  link.addEventListener('click', ()=> menuClick())
})