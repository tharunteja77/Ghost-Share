const toast = {
  container: null,

  createContainer() {
    this.container = document.createElement("div");
    this.container.className = "toast-container";
    document.body.appendChild(this.container);
  },

  show(message, type = "success") {
    if (!this.container) this.createContainer();

    const toastEl = document.createElement("div");
    toastEl.className = `toast ${type}`;
    toastEl.textContent = message;

    this.container.appendChild(toastEl);

    setTimeout(() => {
      toastEl.remove();
    }, 3000);
  },

  success(msg) {
    this.show(msg, "success");
  },

  error(msg) {
    this.show(msg, "error");
  }
};


