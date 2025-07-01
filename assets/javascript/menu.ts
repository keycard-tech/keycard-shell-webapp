const menu = document.getElementById("menu-fixed") as HTMLDivElement;
const buyBtn = document.getElementById("kpro_web__menu-element-keycard-buy") as HTMLButtonElement;
const mobileMenuLink = document.getElementById("mobile-menu-link") as HTMLDivElement;
const mobileMenuImg = document.getElementById("mobile-menu-img") as HTMLImageElement;
const closeMenuImg = document.getElementById("close-menu-img") as HTMLImageElement;
const fixedMenu = document.getElementById("menu-fixed") as HTMLImageElement;
const mobileMenu = document.getElementById("mobile-menu-container") as HTMLDivElement;

const menuScrollBgColor = "#FFFFFF0A";
const btnScrollBgColor = "#FF6400";
const btnBgColor = "#FFFFFF14";

function menuScroll() : void {
  if (document.body.scrollTop > 136 || document.documentElement.scrollTop > 136) {
    menu.style.backgroundColor = menuScrollBgColor;
    buyBtn.style.backgroundColor = btnScrollBgColor;
  } else {
    menu.style.backgroundColor = "transparent";
    buyBtn.style.backgroundColor = btnBgColor;
  }
}

function handleMenu() : void {
   window.onscroll = () => menuScroll();
    
   mobileMenuLink.addEventListener("click", () => {
    if(fixedMenu.classList.contains("keycard_shell__menu-fixed-opened")) {
        fixedMenu.classList.remove("keycard_shell__menu-fixed-opened");
        closeMenuImg.classList.add("keycard_shell__display-none");
        mobileMenuImg.classList.remove("keycard_shell__display-none");
        mobileMenu.classList.add("keycard_shell__mobile-menu-hidden");
        document.body.style.overflow = "inherit";
        buyBtn.style.display = "inherit";
    } else {
        fixedMenu.classList.add("keycard_shell__menu-fixed-opened");
        closeMenuImg.classList.remove("keycard_shell__display-none");
        mobileMenuImg.classList.add("keycard_shell__display-none");
        mobileMenu.classList.remove("keycard_shell__mobile-menu-hidden");
        document.body.style.overflow = "hidden";
        buyBtn.style.display = "none";
    }
   }) 
}

handleMenu();

