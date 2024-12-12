document.addEventListener("DOMContentLoaded", () => {
    const img = document.getElementById("pathway-image");
    const container = document.querySelector(".image-container");

    let scale = 1;
    let panX = 0;
    let panY = 0;
    let isPanning = false;
    let startX, startY;

    // Mouse wheel zoom
    container.addEventListener("wheel", (event) => {
        event.preventDefault();
        const { offsetX, offsetY } = event;

        const zoomFactor = event.deltaY > 0 ? 0.9 : 1.1;
        scale *= zoomFactor;

        panX = offsetX - (offsetX - panX) * zoomFactor;
        panY = offsetY - (offsetY - panY) * zoomFactor;

        img.style.transform = `translate(${panX}px, ${panY}px) scale(${scale})`;
    });

    // Mouse down: start panning
    container.addEventListener("mousedown", (event) => {
        isPanning = true;
        startX = event.clientX - panX;
        startY = event.clientY - panY;
        container.style.cursor = "grabbing";
    });

    // Mouse move: update panning
    container.addEventListener("mousemove", (event) => {
        if (!isPanning) return;
        panX = event.clientX - startX;
        panY = event.clientY - startY;
        img.style.transform = `translate(${panX}px, ${panY}px) scale(${scale})`;
    });

    // Mouse up: stop panning
    container.addEventListener("mouseup", () => {
        isPanning = false;
        container.style.cursor = "grab";
    });

    // Mouse leave: stop panning
    container.addEventListener("mouseleave", () => {
        isPanning = false;
        container.style.cursor = "grab";
    });
});