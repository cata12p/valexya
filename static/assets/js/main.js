// // add hovered class to selected list item
// let list = document.querySelectorAll(".navigation li");

// function activeLink() {
//   list.forEach((item) => {
//     item.classList.remove("hovered");
//   });
//   this.classList.add("hovered");
// }

// list.forEach((item) => item.addEventListener("mouseover", activeLink));

// New NAVBAR
var computedStyle = getComputedStyle(document.documentElement);

var nav = document.getElementById('main-nav');
var mainContent = document.getElementById('main-content');

nav.addEventListener('mouseenter', function() {
    var mainNavigationWidthOpened = parseFloat(computedStyle.getPropertyValue('--main-navigation-width-opened'));
    var mainContentWidth = parseFloat(getComputedStyle(mainContent.parentElement).width);
    var newWidth = mainContentWidth - mainNavigationWidthOpened;

    mainContent.style.marginLeft = `160px`;
    mainContent.style.width = `${newWidth}px`;
});

nav.addEventListener('mouseleave', function() {
    mainContent.style.width = computedStyle.getPropertyValue('--main-width');
    mainContent.style.marginLeft = `0px`;
});