function bindImageModal() {
  const modal = document.getElementById("image-modal");
  const modalImg = document.getElementById("image-modal-img");
  const modalCaption = document.getElementById("image-modal-caption");
  const closeButton = document.getElementById("image-modal-close");
  if (!modal || !modalImg || !modalCaption || !closeButton) return;

  document.querySelectorAll("figure img").forEach((img) => {
    img.addEventListener("click", () => {
      modalImg.src = img.src;
      modalImg.alt = img.alt || "";
      const caption = img.closest("figure")?.querySelector("figcaption")?.textContent;
      modalCaption.textContent = caption || img.alt || "Figure";
      modal.classList.add("open");
      modal.setAttribute("aria-hidden", "false");
    });
  });

  const closeModal = () => {
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
    modalImg.src = "";
  };

  closeButton.addEventListener("click", closeModal);
  modal.addEventListener("click", (event) => {
    if (event.target === modal) closeModal();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && modal.classList.contains("open")) closeModal();
  });
}

bindImageModal();
