const menu = document.getElementById("menu-fixed") as HTMLDivElement;
const buyBtn = document.getElementById("kpro_web__menu-element-keycard-buy") as HTMLButtonElement;
const mobileMenuLink = document.getElementById("mobile-menu-link") as HTMLDivElement;
const mobileMenuImg = document.getElementById("mobile-menu-img") as HTMLImageElement;
const closeMenuImg = document.getElementById("close-menu-img") as HTMLImageElement;
const fixedMenu = document.getElementById("menu-fixed") as HTMLImageElement;
const mobileMenu = document.getElementById("mobile-menu-container") as HTMLDivElement;

const bottomContainer = document.getElementById("bottom-content-container") as HTMLDivElement;
const bottomHeading = document.getElementById("bottom-heading") as HTMLDivElement;
const updateShell = document.getElementById("update") as HTMLDivElement;  
const verifyDevice = document.getElementById("verify") as HTMLDivElement;
const nextSteps = document.getElementsByClassName("keycard_shell__steps");

const menuScrollBgColor = "#FFFFFF0A";
const btnScrollBgColor = "#FF6400";
const btnBgColor = "#FFFFFF14";
const headerHeigth = 136;
const minResizeScreenWidth = 959;

function menuScroll() : void {
  if (document.body.scrollTop > headerHeigth || document.documentElement.scrollTop > headerHeigth) {
    menu.style.backgroundColor = menuScrollBgColor;
    buyBtn.style.backgroundColor = btnScrollBgColor;
  } else {
    menu.style.backgroundColor = "transparent";
    buyBtn.style.backgroundColor = btnBgColor;
  }
}

function resetMenu() : void {
    if((window.innerWidth > minResizeScreenWidth) && fixedMenu.classList.contains("keycard_shell__menu-fixed-opened")) {
        fixedMenu.classList.remove("keycard_shell__menu-fixed-opened");
        closeMenuImg.classList.add("keycard_shell__display-none");
        mobileMenuImg.classList.remove("keycard_shell__display-none");
        mobileMenu.classList.add("keycard_shell__mobile-menu-hidden");
        document.body.style.overflow = "inherit";
        buyBtn.style.display = "inherit";
    }
}

function resizeBottomMenu() : void {
    if(window.innerWidth < minResizeScreenWidth) {
        bottomContainer.style.flexDirection = "column-reverse";
    } else {
        bottomContainer.style.flexDirection = "row-reverse";
    }
}

function hideBottomMenuSection() : void {
    const currentPath = location.pathname;

    Array.from(nextSteps).forEach((step) => {
        currentPath.includes(step.id) ? step.classList.add("keycard_shell__hide") : step.classList.remove("keycard_shell__hide");
    });
}

async function handleBaseUI() : Promise<void> {
    hideBottomMenuSection();

    window.onscroll = () => menuScroll();
    window.onresize = () => resetMenu();

    mobileMenuLink.addEventListener("click", () => {
    if(fixedMenu.classList.contains("keycard_shell__menu-fixed-opened")) {
        fixedMenu.classList.remove("keycard_shell__menu-fixed-opened");
        closeMenuImg.classList.add("keycard_shell__display-none");
        mobileMenuImg.classList.remove("keycard_shell__display-none");
        mobileMenu.classList.remove("keycard_shell__mobile-menu-opened");
        mobileMenu.classList.add("keycard_shell__mobile-menu-hidden");
        document.body.style.overflow = "inherit";
        buyBtn.style.display = "inherit";
    } else {
        fixedMenu.classList.add("keycard_shell__menu-fixed-opened");
        closeMenuImg.classList.remove("keycard_shell__display-none");
        mobileMenu.classList.add("keycard_shell__mobile-menu-opened");
        mobileMenuImg.classList.add("keycard_shell__display-none");
        mobileMenu.classList.remove("keycard_shell__mobile-menu-hidden");
        document.body.style.overflow = "hidden";
        buyBtn.style.display = "none";
    }
   }); 

    bottomHeading.classList.remove('keycard_shell__display-none');
    updateShell.classList.remove('keycard_shell__display-none');
    verifyDevice.classList.remove('keycard_shell__display-none');
}

handleBaseUI();


