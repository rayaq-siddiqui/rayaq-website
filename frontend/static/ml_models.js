// Turns a figure with several [data-ml-step] panels into a one-at-a-time slider.
// Without this script every panel stays visible, so pages read fully with JS off.
(function () {
  document.querySelectorAll("[data-ml-steps]").forEach(function (figure) {
    var steps = Array.prototype.slice.call(figure.querySelectorAll("[data-ml-step]"));
    if (steps.length < 2) return;

    var controls = document.createElement("div");
    controls.className = "ml-steps-controls";
    var input = document.createElement("input");
    input.type = "range";
    input.min = "0";
    input.max = String(steps.length - 1);
    input.value = "0";
    input.setAttribute("aria-label", figure.getAttribute("data-ml-steps") || "Step");
    var label = document.createElement("output");
    controls.appendChild(input);
    controls.appendChild(label);
    figure.insertBefore(controls, figure.firstChild);
    figure.classList.add("ml-steps-active");

    function show(index) {
      steps.forEach(function (step, i) {
        step.hidden = i !== index;
      });
      label.textContent = steps[index].getAttribute("data-ml-step");
    }

    input.addEventListener("input", function () {
      show(Number(input.value));
    });
    show(0);
  });
})();
