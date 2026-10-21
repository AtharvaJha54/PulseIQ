window.addEventListener("load", () => {

    const sphere = document.querySelector(".sphere");

    sphere.animate(
        [
            {
                transform: "scale(0)",
                opacity: 0
            },
            {
                transform: "scale(1)",
                opacity: 1
            }
        ],
        {
            duration: 1000,
            easing: "ease-out",
            fill: "forwards"
        }
    );})
