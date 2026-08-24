(function () {
  "use strict";

  var defaults = window.FLIGHTS_DEFAULTS || {};
  var form = document.getElementById("search-form");
  var results = document.getElementById("results");
  var formError = document.getElementById("form-error");
  var submitButton = document.getElementById("submit-button");

  var LOADING_MESSAGES = [
    "Checking recent fares…",
    "Comparing flexible dates…",
    "Finding the cheapest combinations…",
  ];

  var loadingTimer = null;

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) {
      node.className = className;
    }
    if (text !== undefined && text !== null) {
      node.textContent = String(text);
    }
    return node;
  }

  function parseDate(value) {
    var parts = String(value || "").split("-");
    if (parts.length !== 3) {
      return null;
    }
    return new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
  }

  function formatDate(value) {
    var date = parseDate(value);
    if (!date) {
      return String(value || "");
    }
    return date.toLocaleDateString(undefined, {
      weekday: "short",
      month: "short",
      day: "numeric",
    });
  }

  function formatMoney(amount) {
    var rounded = Math.round(Number(amount));
    return "$" + rounded.toLocaleString();
  }

  function relativeTime(isoString) {
    var then = Date.parse(isoString);
    if (isNaN(then)) {
      return null;
    }
    var minutes = Math.round((Date.now() - then) / 60000);
    if (minutes < 2) {
      return "just now";
    }
    if (minutes < 60) {
      return minutes + " minutes ago";
    }
    var hours = Math.round(minutes / 60);
    if (hours < 24) {
      return hours === 1 ? "an hour ago" : hours + " hours ago";
    }
    var days = Math.round(hours / 24);
    return days === 1 ? "a day ago" : days + " days ago";
  }

  function safeUrl(value) {
    return typeof value === "string" && value.indexOf("https://") === 0 ? value : null;
  }

  function clear(node) {
    while (node.firstChild) {
      node.removeChild(node.firstChild);
    }
  }

  function showError(message) {
    formError.textContent = message;
    formError.hidden = !message;
  }

  function setupCombo(name) {
    var wrapper = document.querySelector('[data-combo="' + name + '"]');
    var input = document.getElementById(name + "-input");
    var hidden = document.getElementById(name + "-code");
    var list = document.getElementById(name + "-options");
    var options = [];
    var activeIndex = -1;
    var requestTimer = null;

    function close() {
      list.hidden = true;
      input.setAttribute("aria-expanded", "false");
      activeIndex = -1;
      options = [];
      clear(list);
    }

    function choose(entry) {
      hidden.value = entry.code;
      input.value = entry.type === "city" ? entry.city : entry.city + " (" + entry.code + ")";
      close();
    }

    function highlight(index) {
      var items = list.querySelectorAll(".combo-option");
      for (var i = 0; i < items.length; i += 1) {
        items[i].classList.toggle("active", i === index);
      }
      if (index >= 0 && items[index]) {
        items[index].scrollIntoView({ block: "nearest" });
      }
      activeIndex = index;
    }

    function render(entries) {
      clear(list);
      options = entries;
      if (!entries.length) {
        close();
        return;
      }

      entries.forEach(function (entry, index) {
        var item = el("li", "combo-option");
        item.setAttribute("role", "option");
        item.appendChild(el("span", "combo-option-code", entry.code));

        var text = el("div", "combo-option-text");
        text.appendChild(el("div", "combo-option-city", entry.city));
        text.appendChild(el("div", "combo-option-name", entry.name + " · " + entry.country));
        item.appendChild(text);

        item.addEventListener("mousedown", function (event) {
          event.preventDefault();
          choose(entry);
        });
        item.addEventListener("mouseenter", function () {
          highlight(index);
        });
        list.appendChild(item);
      });

      list.hidden = false;
      input.setAttribute("aria-expanded", "true");
      activeIndex = -1;
    }

    function lookup(query) {
      return fetch("/api/flights/airports?q=" + encodeURIComponent(query))
        .then(function (response) {
          return response.ok ? response.json() : { results: [] };
        })
        .then(function (payload) {
          return payload.results || [];
        })
        .catch(function () {
          return [];
        });
    }

    input.addEventListener("input", function () {
      hidden.value = "";
      window.clearTimeout(requestTimer);
      var query = input.value.trim();
      if (query.length < 2) {
        close();
        return;
      }
      requestTimer = window.setTimeout(function () {
        lookup(query).then(render);
      }, 140);
    });

    input.addEventListener("keydown", function (event) {
      if (list.hidden) {
        return;
      }
      if (event.key === "ArrowDown") {
        event.preventDefault();
        highlight((activeIndex + 1) % options.length);
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        highlight(activeIndex <= 0 ? options.length - 1 : activeIndex - 1);
      } else if (event.key === "Enter" && activeIndex >= 0) {
        event.preventDefault();
        choose(options[activeIndex]);
      } else if (event.key === "Escape") {
        close();
      }
    });

    input.addEventListener("blur", function () {
      window.setTimeout(close, 120);
    });

    document.addEventListener("click", function (event) {
      if (!wrapper.contains(event.target)) {
        close();
      }
    });

    return {
      code: function () {
        return hidden.value;
      },
      text: function () {
        return input.value.trim();
      },
      resolve: function () {
        if (hidden.value) {
          return Promise.resolve(hidden.value);
        }
        var typed = input.value.trim();
        if (!typed) {
          return Promise.resolve("");
        }
        return lookup(typed).then(function (entries) {
          if (!entries.length) {
            return "";
          }
          choose(entries[0]);
          return entries[0].code;
        });
      },
      set: function (code) {
        return lookup(code).then(function (entries) {
          var match = entries.filter(function (entry) {
            return entry.code === code;
          })[0];
          if (match) {
            choose(match);
          }
        });
      },
    };
  }

  function checkProviderStatus() {
    var banner = document.getElementById("provider-notice");
    fetch("/api/flights/health")
      .then(function (response) {
        return response.ok ? response.json() : null;
      })
      .then(function (payload) {
        if (!payload || payload.providerConfigured) {
          return;
        }
        clear(banner);
        banner.appendChild(el("span", "insight-bullet", "ℹ"));
        var text = el("div");
        text.appendChild(el("strong", null, "Live search isn't switched on yet. "));
        text.appendChild(
          document.createTextNode(
            "The site owner hasn't connected a flight-data provider, so searches below won't return results yet."
          )
        );
        banner.appendChild(text);
        banner.hidden = false;
      })
      .catch(function () {});
  }

  checkProviderStatus();

  var origin = setupCombo("origin");
  var destination = setupCombo("destination");

  function stopLoading() {
    if (loadingTimer) {
      window.clearInterval(loadingTimer);
      loadingTimer = null;
    }
  }

  function renderLoading() {
    stopLoading();
    clear(results);

    var status = el("p", "loading-status", LOADING_MESSAGES[0]);
    results.appendChild(status);

    for (var i = 0; i < 3; i += 1) {
      var skeleton = el("div", "skeleton");
      skeleton.appendChild(el("div", "skeleton-line tall"));
      skeleton.appendChild(el("div", "skeleton-line medium"));
      skeleton.appendChild(el("div", "skeleton-line short"));
      results.appendChild(skeleton);
    }

    var index = 0;
    loadingTimer = window.setInterval(function () {
      index = (index + 1) % LOADING_MESSAGES.length;
      status.textContent = LOADING_MESSAGES[index];
    }, 1400);
  }

  function noticeNode(payload) {
    var stale = payload.metadata && payload.metadata.stale;
    var notice = el("div", stale ? "notice notice-warn" : "notice");
    notice.appendChild(el("span", "insight-bullet", stale ? "⚠" : "ℹ"));

    var text = el("div");
    if (stale) {
      text.appendChild(el("strong", null, "Older prices. "));
      text.appendChild(document.createTextNode(payload.message));
    } else {
      text.appendChild(el("strong", null, "Indicative price. "));
      text.appendChild(document.createTextNode(payload.freshnessMessage || ""));
    }

    var age = relativeTime(payload.searchedAt);
    if (age) {
      text.appendChild(document.createTextNode(" Last checked " + age + "."));
    }

    notice.appendChild(text);
    return notice;
  }

  function metaTags(candidate) {
    var meta = el("div", "deal-meta");
    if (candidate.nights !== null && candidate.nights !== undefined) {
      meta.appendChild(el("span", "tag", candidate.nights + " nights"));
    }
    if (candidate.stops === 0) {
      meta.appendChild(el("span", "tag tag-direct", "Direct"));
    } else if (typeof candidate.stops === "number") {
      meta.appendChild(el("span", "tag", candidate.stops === 1 ? "1 stop" : candidate.stops + " stops"));
    }
    if (candidate.airlineCode) {
      meta.appendChild(el("span", "tag", candidate.airlineCode));
    }
    var observed = relativeTime(candidate.foundAt);
    if (observed) {
      meta.appendChild(el("span", "tag", "Seen " + observed));
    }
    return meta;
  }

  function datesNode(candidate) {
    var dates = el("div", "deal-dates");
    dates.appendChild(el("span", null, formatDate(candidate.departureDate)));
    dates.appendChild(el("span", "deal-arrow", "→"));
    dates.appendChild(el("span", null, formatDate(candidate.returnDate)));
    return dates;
  }

  function verifyLink(candidate, className, label) {
    var url = safeUrl(candidate.bookingUrl);
    if (!url) {
      return null;
    }
    var link = el("a", className, label);
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    return link;
  }

  function bestCard(payload) {
    var candidate = payload.best;
    var card = el("section", "best-card");
    card.appendChild(el("p", "best-eyebrow", "Best deal"));

    var price = el("p", "best-price", formatMoney(candidate.totalPrice));
    price.appendChild(el("span", "currency-code", candidate.currency));
    card.appendChild(price);

    card.appendChild(
      el(
        "p",
        "best-route",
        payload.places.origin.label + " → " + payload.places.destination.label
      )
    );
    card.appendChild(datesNode(candidate));
    card.appendChild(metaTags(candidate));

    var link = verifyLink(candidate, "verify-link", "Check current price");
    if (link) {
      card.appendChild(link);
    }
    return card;
  }

  function dateStrip(payload) {
    if (!payload.datePrices || payload.datePrices.length < 2) {
      return null;
    }

    var prices = payload.datePrices.map(function (entry) {
      return entry.price;
    });
    var lowest = Math.min.apply(null, prices);
    var highest = Math.max.apply(null, prices);
    var span = Math.max(highest - lowest, 1);

    var panel = el("section", "panel");
    panel.appendChild(el("h2", null, "Cheapest by departure day"));

    var strip = el("div", "date-strip");
    payload.datePrices.forEach(function (entry) {
      var column = el("div", "date-column");
      if (entry.price === lowest) {
        column.classList.add("cheapest");
      }

      var track = el("div", "date-bar-track");
      var bar = el("div", "date-bar");
      bar.style.height = Math.round(28 + ((entry.price - lowest) / span) * 68) + "%";
      track.appendChild(bar);

      column.appendChild(el("div", "date-price", formatMoney(entry.price)));
      column.appendChild(track);
      column.appendChild(el("div", "date-label", entry.weekday + "\n" + entry.label));
      strip.appendChild(column);
    });

    panel.appendChild(strip);
    return panel;
  }

  function insightsPanel(payload) {
    if (!payload.insights || !payload.insights.length) {
      return null;
    }
    var panel = el("section", "panel");
    panel.appendChild(el("h2", null, "What the prices suggest"));

    var list = el("ul", "insight-list");
    payload.insights.forEach(function (insight) {
      var item = el("li");
      item.appendChild(el("span", "insight-bullet", "•"));
      item.appendChild(el("span", null, insight.message));
      list.appendChild(item);
    });

    panel.appendChild(list);
    return panel;
  }

  function alternativesPanel(payload) {
    var rest = payload.candidates.slice(1);
    if (!rest.length) {
      return null;
    }

    var panel = el("section", "panel");
    panel.appendChild(el("h2", null, "Other cheap options"));

    var list = el("ul", "deal-list");
    rest.forEach(function (candidate) {
      var item = el("li", "deal-item");
      item.appendChild(datesNode(candidate));
      item.appendChild(
        el("div", "deal-item-price", formatMoney(candidate.totalPrice) + " " + candidate.currency)
      );
      item.appendChild(metaTags(candidate));

      var link = verifyLink(candidate, "deal-item-link", "Check current price →");
      if (link) {
        item.appendChild(link);
      }
      list.appendChild(item);
    });

    panel.appendChild(list);
    return panel;
  }

  function emptyState(message) {
    var block = el("section", "empty-state");
    block.appendChild(el("h2", null, "No fares found"));
    block.appendChild(
      el(
        "p",
        null,
        message || "We couldn't find a recently observed fare for this route and date window."
      )
    );

    var suggestions = el("ul");
    ["Widen the departure window", "Allow more trip lengths", "Try a nearby airport"].forEach(
      function (text) {
        suggestions.appendChild(el("li", null, "• " + text));
      }
    );
    block.appendChild(suggestions);
    return block;
  }

  function renderResults(payload) {
    stopLoading();
    clear(results);

    if (!payload.candidates.length) {
      results.appendChild(emptyState(payload.message));
      return;
    }

    results.appendChild(noticeNode(payload));
    results.appendChild(bestCard(payload));

    [insightsPanel(payload), dateStrip(payload), alternativesPanel(payload)].forEach(function (
      node
    ) {
      if (node) {
        results.appendChild(node);
      }
    });
  }

  function renderFailure(message) {
    stopLoading();
    clear(results);
    var notice = el("div", "notice notice-warn");
    notice.appendChild(el("span", "insight-bullet", "⚠"));
    notice.appendChild(el("div", null, message));
    results.appendChild(notice);
  }

  function readForm(originCode, destinationCode) {
    return {
      origin: originCode,
      destination: destinationCode,
      earliestDeparture: document.getElementById("earliest-departure").value,
      latestDeparture: document.getElementById("latest-departure").value,
      minNights: Number(document.getElementById("min-nights").value),
      maxNights: Number(document.getElementById("max-nights").value),
      currency: document.getElementById("currency").value,
      directOnly: document.getElementById("direct-only").checked,
    };
  }

  function submitSearch(body) {
    submitButton.disabled = true;
    submitButton.textContent = "Searching…";
    renderLoading();

    return fetch("/api/flights/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
      .then(function (response) {
        return response.json().then(function (payload) {
          return { ok: response.ok, payload: payload };
        });
      })
      .then(function (result) {
        if (result.ok) {
          renderResults(result.payload);
        } else {
          showError(result.payload.error || "Something went wrong. Try again.");
          renderFailure(result.payload.error || "Something went wrong. Try again.");
        }
      })
      .catch(function () {
        renderFailure("We couldn't reach the search service. Check your connection and try again.");
      })
      .then(function () {
        submitButton.disabled = false;
        submitButton.textContent = "Find cheap flights";
      });
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    showError("");

    Promise.all([origin.resolve(), destination.resolve()]).then(function (codes) {
      if (!codes[0]) {
        showError("Pick where you are flying from.");
        return;
      }
      if (!codes[1]) {
        showError("Pick where you are flying to.");
        return;
      }
      submitSearch(readForm(codes[0], codes[1]));
    });
  });

  document.getElementById("swap-button").addEventListener("click", function () {
    var originCode = origin.code();
    var destinationCode = destination.code();
    if (!originCode || !destinationCode) {
      return;
    }
    origin.set(destinationCode);
    destination.set(originCode);
  });

  Array.prototype.forEach.call(document.querySelectorAll(".chip"), function (chip) {
    chip.addEventListener("click", function () {
      showError("");
      Promise.all([
        origin.set(chip.getAttribute("data-origin")),
        destination.set(chip.getAttribute("data-destination")),
      ]).then(function () {
        form.dispatchEvent(new Event("submit", { cancelable: true }));
      });
    });
  });

  if (defaults.directOnly) {
    document.getElementById("direct-only").checked = true;
  }
})();
