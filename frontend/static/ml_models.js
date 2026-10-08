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

// Recomputes the attention table from the page's own q, k, v so readers can toggle the mask,
// the 1/sqrt(d) scale and a softmax temperature. The server-rendered tables stay as the fallback.
(function () {
  document.querySelectorAll("[data-ml-attention]").forEach(function (root) {
    var tokens = JSON.parse(root.getAttribute("data-tokens"));
    var queries = JSON.parse(root.getAttribute("data-queries"));
    var keys = JSON.parse(root.getAttribute("data-keys"));
    var values = JSON.parse(root.getAttribute("data-values"));
    var fallback = root.querySelector("[data-ml-attention-static]");
    if (fallback) fallback.hidden = true;

    var state = { causal: false, scaled: true, temperature: 1, row: 2 };

    var controls = document.createElement("div");
    controls.className = "ml-attn-controls";
    controls.innerHTML =
      '<label><input type="checkbox" data-key="causal"> Causal mask</label>' +
      '<label><input type="checkbox" data-key="scaled" checked> Divide by √d</label>' +
      '<label class="ml-attn-temp">Temperature <input type="range" min="0.2" max="3" step="0.1" value="1" data-key="temperature"> <output>1.0</output></label>';
    root.appendChild(controls);

    var table = document.createElement("table");
    table.className = "ml-heatmap ml-heatmap-live";
    var wrap = document.createElement("div");
    wrap.className = "jj-table-wrap";
    wrap.appendChild(table);
    root.appendChild(wrap);

    var readout = document.createElement("p");
    readout.className = "ml-caption";
    readout.setAttribute("aria-live", "polite");
    root.appendChild(readout);

    function dot(a, b) {
      return a.reduce(function (sum, x, i) { return sum + x * b[i]; }, 0);
    }

    function compute() {
      var d = queries[0].length;
      return queries.map(function (q, i) {
        var scores = keys.map(function (k, j) {
          if (state.causal && j > i) return null;
          var s = dot(q, k);
          if (state.scaled) s /= Math.sqrt(d);
          return s / state.temperature;
        });
        var live = scores.filter(function (s) { return s !== null; });
        var top = Math.max.apply(null, live);
        var exps = scores.map(function (s) { return s === null ? 0 : Math.exp(s - top); });
        var total = exps.reduce(function (a, b) { return a + b; }, 0);
        return exps.map(function (e) { return e / total; });
      });
    }

    function render() {
      var weights = compute();
      var head = "<thead><tr><th></th>" + tokens.map(function (t) { return "<th>" + t + "</th>"; }).join("") + "</tr></thead>";
      var body = weights.map(function (row, i) {
        var cells = row.map(function (w, j) {
          var masked = state.causal && j > i;
          return '<td style="background: rgba(77, 163, 255, ' + (w * 0.85).toFixed(2) + ')">' + (masked ? "—" : w.toFixed(2)) + "</td>";
        }).join("");
        var selected = i === state.row ? ' class="ml-row-selected"' : "";
        return "<tr" + selected + '><th><button type="button" data-row="' + i + '">' + tokens[i] + "</button></th>" + cells + "</tr>";
      }).join("");
      table.innerHTML = head + "<tbody>" + body + "</tbody>";

      var row = weights[state.row];
      var output = values[0].map(function (_, c) {
        return row.reduce(function (sum, w, j) { return sum + w * values[j][c]; }, 0);
      });
      var best = row.indexOf(Math.max.apply(null, row));
      readout.textContent = "“" + tokens[state.row] + "” reads " + Math.round(row[best] * 100) + "% from “" + tokens[best] +
        "”. Its output is [" + output.map(function (x) { return x.toFixed(2); }).join(", ") + "]. Click a row's token to follow it.";
    }

    controls.addEventListener("input", function (event) {
      var key = event.target.getAttribute("data-key");
      if (key === "temperature") {
        state.temperature = Number(event.target.value);
        event.target.nextElementSibling.textContent = state.temperature.toFixed(1);
      } else if (key) {
        state[key] = event.target.checked;
      }
      render();
    });
    table.addEventListener("click", function (event) {
      var button = event.target.closest("button[data-row]");
      if (!button) return;
      state.row = Number(button.getAttribute("data-row"));
      render();
    });
    render();
  });
})();

// A parameter calculator for nn.Transformer, using the same formulas as the worked example.
(function () {
  document.querySelectorAll("[data-ml-params]").forEach(function (root) {
    root.hidden = false;
    var fields = [
      ["d_model", 512, 8, 8192], ["nhead", 8, 1, 128], ["encoder layers", 6, 0, 96],
      ["decoder layers", 6, 0, 96], ["dim_feedforward", 2048, 8, 65536]
    ];
    root.innerHTML = '<p class="ml-caption">Try your own sizes:</p><div class="ml-calc-fields">' + fields.map(function (f, i) {
      return '<label>' + f[0] + ' <input type="number" inputmode="numeric" value="' + f[1] + '" min="' + f[2] + '" max="' + f[3] + '" data-i="' + i + '"></label>';
    }).join("") + '</div><p class="ml-calc-result" aria-live="polite"></p>';
    var result = root.querySelector(".ml-calc-result");

    function update() {
      var v = Array.prototype.map.call(root.querySelectorAll("input"), function (input) { return Number(input.value) || 0; });
      var d = v[0], heads = v[1], enc = v[2], dec = v[3], ff = v[4];
      if (heads < 1 || d % heads !== 0) {
        result.textContent = "d_model must be divisible by nhead (PyTorch asserts this).";
        return;
      }
      var attn = 4 * d * d + 4 * d, ffn = 2 * d * ff + ff + d, norm = 2 * d;
      var encLayer = attn + ffn + 2 * norm, decLayer = 2 * attn + ffn + 3 * norm;
      var total = enc * encLayer + norm + dec * decLayer + norm;
      result.innerHTML = "Encoder layer <strong>" + encLayer.toLocaleString("en-US") + "</strong> · decoder layer <strong>" +
        decLayer.toLocaleString("en-US") + "</strong> · total <strong>" + total.toLocaleString("en-US") +
        "</strong> (≈" + (total / 1e6).toFixed(1) + "M, head dim " + d / heads + ")";
    }
    root.addEventListener("input", update);
    update();
  });
})();
