/* Inclusive Reading Assistant — accessible UI and API integration. No secrets. */
const API_BASE = "http://127.0.0.1:8000"; // FastAPI local backend; do not put API keys here.

        const SAMPLE = "Cognitive load theory posits that working memory has a limited capacity, which constrains the amount of novel information a learner can process simultaneously. Consequently, instructional design should minimise extraneous load, thereby freeing cognitive resources for germane processing. Empirical evidence indicates that learners with substantial prior knowledge exhibit reduced susceptibility to these constraints.";

        const TERMS = [
            "working memory",
            "extraneous load",
            "germane processing",
            "empirical evidence",
            "prior knowledge",
            "cognitive load",
            "digital divide",
            "critical thinking",
            "independent learning",
            "student engagement"
        ];

        const $ = id => document.getElementById(id);
        const W = $("wrap");

        const st = {
            orig: "",
            res: [],
            hl: false,
            busy: false,
            failures: 0
        };

        const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        }[c]));
        function termize(html) {
            if (!st.hl || !st.orig) return html;

            return TERMS
                .filter(term => st.orig.toLowerCase().includes(term.toLowerCase()))
                .sort((a, b) => b.length - a.length)
                .reduce((result, term) => {
                    const regex = new RegExp(
                        "\\b(" + term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")\\b(?![^<]*>)",
                        "gi"
                    );

                    return result.replace(
                        regex,
                        match => `<button class="term" data-t="${esc(match)}" aria-label="Explain term ${esc(match)}" title="Explain this term">${match}</button>`
                    );
                }, html);
        } function txt(raw) {
            const safe = esc(raw);
            return `<span class="txt" data-raw="${safe}">${termize(safe)}</span>`;
        }

        function paintTerms() {
            document.querySelectorAll(".txt").forEach(element => {
                element.innerHTML = termize(element.dataset.raw || "");
            });
        }

        function add(role, html) {
            const message = document.createElement("div");
            message.className = "m " + (role === "u" ? "u" : "a");

            const bubble = document.createElement("div");
            bubble.className = "b";
            bubble.innerHTML = html;

            message.appendChild(bubble);
            W.appendChild(message);

            $("msgs").scrollTop = $("msgs").scrollHeight;
            return message;
        }

        function chips(list) {
            return `<div class="bar">${list.map(([action, label, extra]) =>
                `<button data-act="${action}" ${extra ? `data-x="${extra}"` : ""}>${label}</button>`
            ).join("")}</div>`;
        }

        function setBusy(value) {
            st.busy = value;
            $("send").disabled = value;
            $("upBtn").disabled = value;
            $("send").textContent = value ? "Waiting..." : "Send";
        }

        function showLoading(label) {
            return add("a", `<div class="banner">Processing ${esc(label)} with Gemini... Please wait.</div>`);
        }

        async function apiRequest(endpoint, payload) {
            let response;

            try {
                response = await fetch(`${API_BASE}/${endpoint}`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        ...payload,
                        user_action: true
                    })
                });
            } catch (error) {
                throw new Error(
                    "Cannot connect to the backend. Make sure FastAPI is running at " +
                    API_BASE + "."
                );
            }

            let data;

            try {
                data = await response.json();
            } catch {
                throw new Error("The backend returned an invalid response.");
            }

            if (!response.ok) {
                throw new Error(data.detail || `Request failed (${response.status}).`);
            }

            return data;
        }

        function check(text) {
            if (!text.trim()) {
                return "That is empty, so there is nothing to work on. Paste or type some English text.";
            }

            if (text.trim().length < 25) {
                return "That is very short. Add a full sentence or two so the result is meaningful.";
            }

            const letters = text.replace(/[^\p{L}]/gu, "");
            const english = letters.replace(/[^A-Za-z]/g, "");

            if (letters.length && english.length / letters.length < 0.7) {
                return "This assistant currently supports English text only.";
            }

            return "";
        }

        function vers() {
            $("vers").innerHTML = st.res.length
                ? '<div class="ver">Original (always kept)</div>' +
                st.res.map((result, index) =>
                    `<div class="ver">v${index + 1}: ${esc(result.label)}</div>`
                ).join("")
                : "None yet. The original is always kept.";
        }

        function welcome() {
            W.innerHTML = "";
            st.orig = "";
            st.res = [];
            st.hl = false;
            st.failures = 0;
            $("fExp").checked = false;
            $("fSim").checked = false;
            $("fSum").checked = false;
            vers();
            updateSource();
            const heading = `
                <div class="welcome-shell">
                  <div class="welcome-visual" aria-hidden="true">
                    <div class="orb orb-one"></div><div class="orb orb-two"></div>
                    <div class="visual-paper"><span></span><span></span><span></span><span></span></div>
                    <div class="visual-spark">✦</div>
                  </div>
                  <span class="eyebrow">YOUR READING WORKSPACE</span>
                  <h2>Read with clarity.<br><em>Stay in control.</em></h2>
                  <p class="welcome-lede">Hi! Paste an academic text or upload a TXT/MD file. I can <strong>simplify, summarize, and explain</strong> English academic passages.</p>
                  <div class="welcome-promise"><span class="promise-icon" aria-hidden="true">✓</span><span><strong>You're always in charge.</strong> I won't change anything or call AI until you choose an action. Your original text stays available.</span></div>
                  <p class="welcome-limits">AI answers can be wrong. This demo cannot verify sources or read PDFs and images. Always compare results with your original text.</p>
                  <div class="welcome-next"><span class="next-line"></span><span>START HERE</span><span class="next-line"></span></div>
                  ${chips([["sample", "Try sample passage"], ["help", "Get help"]])}
                </div>`;
            const message = add("a", heading);
            message.classList.add("welcome-message");
        }

        function cfgNow() {
            return {
                sim: $("fSim").checked,
                sum: $("fSum").checked,
                lvl: $("pLvl").value,
                len: Number($("pLen").value)
            };
        }

        async function run(cfg, label) {
            if (!st.orig) {
                add("a", "I need some text first. Paste or upload your text.");
                return;
            }

            const operations = [];

            if (cfg.sim) operations.push("simplify");
            if (cfg.sum) operations.push("summarize");

            if (!operations.length) {
                add("a", "No operation selected. Your original text remains unchanged.");
                return;
            }

            if (st.busy) return;

            setBusy(true);
            const loading = showLoading(label);

            try {
                const results = [];

                // Execute only the operations explicitly selected by the user.
                for (const operation of operations) {
                    if (operation === "simplify") {
                        const data = await apiRequest("simplify", {
                            text: st.orig,
                            level: cfg.lvl
                        });

                        results.push({
                            title: "Simplified",
                            text: data.simplified_text
                        });
                    }

                    if (operation === "summarize") {
                        const data = await apiRequest("summarize", {
                            text: st.orig,
                            length: cfg.len
                        });

                        results.push({
                            title: "Summary",
                            text: data.summary
                        });
                    }
                }

                if (results.some(result => typeof result.text !== "string" || !result.text.trim())) {
                    throw new Error("The AI returned an empty result. Please try again.");
                }

                loading.remove();

                const html =
                    `<div class="banner">AI-generated draft. It may contain mistakes. Please check it against the original.</div>` +
                    results.map(result =>
                        `<h3>${result.title}</h3>${txt(result.text)}`
                    ).join("") +
                    `<div class="orig"><h3>Original</h3>${txt(st.orig)}</div>` +
                    chips([
                        ["orig", "Show original"],
                        ["undo", "Undo"],
                        ["restore", "Restore original"],
                        ["ref", "Simpler", "simpler"],
                        ["ref", "Closer to original", "closer"],
                        ["ref", "Shorter summary", "short"],
                        ["rej", "Not what I wanted"]
                    ]);

                const message = add("a", html);
                message.cfg = { ...cfg };

                st.res.push({
                    el: message,
                    label
                });

                vers();
                st.failures = 0;
                if (tourState.guided) {
                    tourState.guided = false;
                    $("guidedHint").hidden = true;
                    showTour(3);
                }

            } catch (error) {
                loading.remove();

                st.failures += 1;
                const failedMessage = add("a",
                    `<div class="banner">Could not complete the request.</div>` +
                    `${esc(error.message)}` +
                    chips(st.failures >= 2
                        ? [["help", "Get academic support"]]
                        : [["retry", "Try again"], ["help", "Get help"]])
                );
                // Tie Retry to the *failed* request, not the last successful result.
                failedMessage.retryConfig = { ...cfg };
                failedMessage.retryOriginal = st.orig;

                console.error("Backend request error:", error);

            } finally {
                setBusy(false);
            }
        }

        function newText(text, name) {
            const error = check(text);

            if (error) {
                add("a", esc(error) + chips([["help", "Get help"]]));
                return;
            }

            st.orig = text;
            updateSource();
            // Previous result cards are for an older source, not this text.
            st.res.forEach(result => result.el.remove());
            st.res = [];
            st.failures = 0;
            vers();

            if (name) {
                add("u",
                    "📎 " + esc(name) + "\n" +
                    esc(text.slice(0, 200)) +
                    (text.length > 200 ? "…" : "")
                );
            }

            const config = cfgNow();

            // Checkboxes only set preferences. Sending/pasting text never calls AI.
            // A separate click on an action chip is always required.
            add("a",
                `Got your text (${text.trim().split(/\s+/).length} words). What would you like? ` +
                `No AI action runs until you click one of the options below.` +
                chips([
                    ...(config.sim || config.sum ? [["selected", "Run selected actions"]] : []),
                    ["do", "Simplify", "sim"],
                    ["do", "Summarize", "sum"],
                    ["do", "Simplify + Summarize", "both"],
                    ["hl", "Highlight terms to explain"],
                    ["none", "Just keep reading"],
                    ["help", "Help"]
                ])
            );
        }

        function need(callback) {
            if (!st.orig) {
                add("a", "I need some text first. Paste it below or attach a file.");
                return;
            }

            callback();
        }

        function command(text) {
            const value = text.toLowerCase().trim();

            if (value.length > 40) return false;

            const config = cfgNow();

            if (/^(undo|go back)/.test(value)) {
                act("undo");
                return true;
            }

            if (/original/.test(value)) {
                act("restore");
                return true;
            }

            if (/^simplif/.test(value)) {
                need(() => run(
                    { ...config, sim: true, sum: false },
                    "Simplify"
                ));
                return true;
            }

            if (/^summar/.test(value)) {
                need(() => run(
                    { ...config, sim: false, sum: true },
                    "Summarize"
                ));
                return true;
            }

            if (/^(explain|highlight)/.test(value)) {
                need(() => enableHighlights());
                return true;
            }

            return false;
        }
        function enableHighlights() {
            if (!st.orig) {
                add("a", "Please provide some text first.");
                return;
            }

            st.hl = true;
            $("fExp").checked = true;

            paintTerms();

            add("a",
                `<h3>Original text – Click a highlighted term</h3>` +
                `${txt(st.orig)}` +
                `<div class="hint">Click any highlighted term to get an explanation from Gemini.</div>`
            );
        }
        async function explainTerm(term, style = "default") {
            if (!st.orig || st.busy) return;
            term = term.trim();

            if (!st.orig.toLowerCase().includes(term.toLowerCase())) {
                add("a", "This term is not present in the original text. Please select a highlighted term from the original text.");
                return;
            }
            setBusy(true);
            const loading = showLoading("the explanation");

            try {
                const data = await apiRequest("explain", {
                    text: st.orig,
                    term,
                    style
                });

                loading.remove();

                if (!data.explanation) {
                    throw new Error("The AI returned an empty explanation.");
                }

                st.failures = 0;
                add("a",
                    `<h3>${esc(data.term || term)}</h3>` +
                    `${txt(data.explanation)}` +
                    `<div class="banner">AI-generated explanation based on your text. Check your course material.</div>` +
                    (style === "default"
                        ? chips([["example", "Give an example", term]])
                        : "")
                );

            } catch (error) {
                loading.remove();

                st.failures += 1;
                const failedMessage = add("a",
                    `<div class="banner">Could not explain this term.</div>` +
                    `${esc(error.message)}` +
                    chips(st.failures >= 2
                        ? [["help", "Get academic support"]]
                        : [["explainRetry", "Try again", term], ["help", "Get help"]])
                );
                failedMessage.retryStyle = style;
                failedMessage.retryOriginal = st.orig;

                console.error("Explain request error:", error);

            } finally {
                setBusy(false);
            }
        }

        async function act(action, element, extra) {
            if (st.busy) {
                if (action === "restore" || action === "undo") {
                    add("a", "Please wait for the current request to finish before changing versions.");
                }
                return;
            }

            if (action === "sample") {
                add("u", "Sample text");
                newText(SAMPLE);
            }

            else if (action === "selected") {
                const config = cfgNow();
                run(config, "Selected actions");
            }

            else if (action === "do") {
                const config = cfgNow();

                run({
                    ...config,
                    sim: extra !== "sum",
                    sum: extra !== "sim"
                },
                    extra === "both" ? "Simplify + Summarize" :
                        extra === "sim" ? "Simplify" : "Summarize"
                );
            }

            else if (action === "hl") {
                enableHighlights();
            }

            else if (action === "none") {
                add("a", "Okay, your text stays as it is. Ask any time.");
            }

            else if (action === "help") {
                add("a", "I cannot complete this reliably right now. " +
                    "Your original text is unchanged. Check the source passage, " +
                    "or contact your course instructor, teaching assistant, " +
                    "or your faculty's academic/accessibility support office. " +
                    "This demo does not contact a person automatically.");
            }

            else if (action === "undo") {
                const result = st.res.pop();

                if (!result) {
                    add("a", "Nothing to undo. Your original text is still available.");
                    return;
                }

                result.el.remove();
                vers();
                add("a", "Last change undone.");
            }

            else if (action === "restore") {
                if (!st.orig) {
                    add("a", "There is no original text yet. Paste a passage first.");
                    return;
                }
                st.res.forEach(result => result.el.remove());
                st.res = [];
                vers();

                add("a",
                    `<h3>Original text restored</h3>${txt(st.orig)}`
                );
            }

            else if (action === "orig") {
                const original = element.closest(".b").querySelector(".orig");
                original.classList.toggle("on");
                element.textContent = original.classList.contains("on")
                    ? "Hide original"
                    : "Show original";
            }

            else if (action === "ref") {
                const message = element.closest(".m");
                const config = { ...message.cfg };

                if (extra === "short") {
                    if (!config.sum) {
                        add("a", "Summarize is not on for this result. Ask for a summary first.");
                        return;
                    }

                    config.len = 1;
                } else {
                    if (!config.sim) {
                        add("a", "This refinement is for Simplify. Ask me to simplify first.");
                        return;
                    }

                    config.lvl = extra === "simpler" ? "simpler" : "closer";
                }

                run(config, "Refined result");
            }

            else if (action === "rej") {
                element.closest(".b").insertAdjacentHTML(
                    "beforeend",
                    `<div class="bar"><span>What went wrong? (optional)</span></div>` +
                    chips([
                        ["why", "Too complex", "simpler"],
                        ["why", "Changed the meaning", "closer"],
                        ["why", "Too vague", "closer"],
                        ["why", "Just go back", "back"]
                    ])
                );

                element.remove();
            }

            else if (action === "why") {
                const message = element.closest(".m");

                if (extra === "back") {
                    act("undo");
                    return;
                }

                const config = { ...message.cfg, lvl: extra };
                message.querySelector(".bar:last-child")?.remove();

                run(config, "Retry after feedback");
            }

            else if (action === "example") {
                explainTerm(extra, "example");
            }

            else if (action === "explainRetry") {
                const message = element.closest(".m");
                if (message?.retryOriginal === st.orig) {
                    element.disabled = true;
                    explainTerm(extra, message.retryStyle || "default");
                } else {
                    add("a", "This request refers to an earlier text. Select the term again.");
                }
            }

            else if (action === "retry") {
                const message = element.closest(".m");
                if (message?.retryConfig && message.retryOriginal === st.orig) {
                    // A retry is an explicit user action: replay the exact failed choice.
                    element.disabled = true;
                    run({ ...message.retryConfig }, "Retry");
                } else {
                    add("a", "That request is no longer available. Please choose Simplify or Summarize again.");
                }
            }
        }

        W.addEventListener("click", event => {
            const termButton = event.target.closest(".term");

            if (termButton) {
                explainTerm(termButton.dataset.t, "default");
                return;
            }

            const button = event.target.closest("[data-act]");

            if (button) {
                act(button.dataset.act, button, button.dataset.x);
            }
        });

        function send() {
            if (st.busy) return;

            const text = $("inp").value;
            $("inp").value = "";
            $("inp").style.height = "";

            if (!text.trim()) {
                add("a", "Your message is empty. Type or paste something first.");
                return;
            }

            add("u", esc(text.length > 600 ? text.slice(0, 600) + "…" : text));

            if (!command(text)) {
                newText(text);
            }
        }

        $("send").onclick = send;

        $("inp").addEventListener("keydown", event => {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                send();
            }
        });

        $("inp").addEventListener("input", event => {
            event.target.style.height = "auto";
            event.target.style.height = event.target.scrollHeight + "px";
        });

        $("upBtn").onclick = () => $("file").click();

        $("file").onchange = event => {
            const file = event.target.files[0];
            event.target.value = "";

            if (!file) return;

            if (!/\.(txt|md)$/i.test(file.name)) {
                add("u", "📎 " + esc(file.name));
                add("a", "This demo reads only .txt and .md files. Please paste the text from your PDF, Word document, or image instead.");
                return;
            }

            const reader = new FileReader();

            reader.onload = () => newText(String(reader.result), file.name);
            reader.onerror = () => add("a", "I could not read that file. Please try another one or paste the text.");

            reader.readAsText(file);
        };

        $("tog").onclick = () => {
            const closed = $("app").classList.toggle("closed");
            $("tog").setAttribute("aria-expanded", !closed);
        };

        $("newChat").onclick = welcome;

        $("fExp").onchange = event => {
            st.hl = event.target.checked;
            paintTerms();
        };

        function fmt() {
            const root = document.documentElement.style;

            root.setProperty("--fs", $("aSize").value + "px");
            root.setProperty("--lh", $("aLH").value / 10);
            root.setProperty("--w", $("aW").value + "ch");
            root.setProperty("--ff", $("aFont").value || "inherit");

            const background = $("aBg").value;

            document.querySelectorAll("#wrap .m.a .b").forEach(bubble => {
                if (background) {
                    const [bg, color] = background.split("|");
                    bubble.style.background = bg;
                    bubble.style.color = color;
                } else {
                    bubble.style.background = "";
                    bubble.style.color = "";
                }
            });

            window.__bg = background;
        }

        ["aFont", "aSize", "aLH", "aW", "aBg"].forEach(id => {
            $(id).oninput = fmt;
        });

        new MutationObserver(() => {
            if (window.__bg) fmt();
        }).observe(W, { childList: true });

        const settingsLayout = window.matchMedia("(max-width: 900px)");
        const updateSettingsForViewport = compact => {
            $("app").classList.toggle("closed", compact);
            $("tog").setAttribute("aria-expanded", String(!compact));
        };
        updateSettingsForViewport(settingsLayout.matches);
        settingsLayout.addEventListener("change", event => updateSettingsForViewport(event.matches));
        $("closeSettings").onclick = () => {
            $("app").classList.add("closed");
            $("tog").setAttribute("aria-expanded", "false");
            $("tog").focus();
        };


        // Nesma Week 6–7: visible original + user-initiated, arbitrary phrase Explain.
        let lastSelectedPhrase = "";
        const tourState = { guided: false, step: 0, lastFocus: null };
        function updateSource() {
            const loaded = !!st.orig;
            $("sourceText").textContent = loaded ? st.orig :
                "Your original passage will appear here. Paste text, attach a TXT/MD file, or try the sample.";
            $("sourceText").classList.toggle("source-placeholder", !loaded);
            $("sourceMeta").textContent = loaded
                ? `${st.orig.trim().split(/\s+/).length} words · Original is never overwritten`
                : "No text loaded yet.";
            $("termInput").value = "";
            lastSelectedPhrase = "";
            $("explainSelection").disabled = !loaded;
        }
        function captureSelection() {
            if (!st.orig) return;
            const selection = window.getSelection();
            if (!selection || selection.isCollapsed || !selection.toString().trim()) return;
            const start = selection.anchorNode, end = selection.focusNode;
            const source = $("sourceText");
            if (!source.contains(start) || !source.contains(end)) return;
            const phrase = selection.toString().trim();
            if (phrase && phrase.length <= 200 && st.orig.toLowerCase().includes(phrase.toLowerCase())) {
                lastSelectedPhrase = phrase;
                $("termInput").value = phrase;
                $("statusMessage").textContent = `Selected: ${phrase}. Click Explain selected phrase to request an AI explanation.`;
            }
        }
        $("sourceText").addEventListener("mouseup", captureSelection);
        $("sourceText").addEventListener("keyup", captureSelection);
        $("sourceText").addEventListener("touchend", captureSelection);
        $("explainSelection").onclick = () => {
            const term = $("termInput").value.trim() || lastSelectedPhrase;
            if (!st.orig) { $("statusMessage").textContent = "Paste text first."; return; }
            if (!term || term.length > 200 || !st.orig.toLowerCase().includes(term.toLowerCase())) {
                $("statusMessage").textContent = "Enter a word or phrase found in your original text (up to 200 characters).";
                $("termInput").focus();
                return;
            }
            $("statusMessage").textContent = `Requesting explanation for: ${term}`;
            explainTerm(term, "default");
        };
        function setSourceOpen(value) {
            $("app").classList.toggle("source-open", value);
            $("openSource").setAttribute("aria-expanded", String(value));
            if (value) $("sourceText").focus(); else $("openSource").focus();
        }
        $("openSource").onclick = () => setSourceOpen(true);
        $("closeSource").onclick = () => setSourceOpen(false);
        $("skipGuided").onclick = () => {
            tourState.guided = false; $("guidedHint").hidden = true; showTour(3);
        };
        // Three-stage onboarding (static demo → guided click → independent use).
        const stages = {
          1: { step:"Stage 1 of 3 · The system does it", title:"See a safe example",
               html:`<p>This is a <strong>fixed teaching example</strong>, not a Gemini answer. You can compare an academic sentence with a clearer version.</p>
                     <div class="tour-static"><div><strong>Original (sample)</strong>Working memory has a finite capacity for novel information.</div>
                     <div><strong>Simplified (static example)</strong>Working memory can handle only a limited amount of new information at once.</div></div>
                     <p class="tour-notice"><strong>Your control starts here:</strong> AI never changes or summarizes your own text until <em>you</em> explicitly request an action. Every generated result can be checked against the original.</p>` },
          2: { step:"Stage 2 of 3 · Co-pilot", title:"Try with guidance",
               html:`<p>Next, we will load a <strong>synthetic sample passage</strong> and guide you to the Simplify action. Loading the sample does <strong>not</strong> call Gemini.</p>
                     <p>You'll choose the action yourself, and can use <strong>Show original</strong>, <strong>Undo</strong> or <strong>Restore original</strong> afterward.</p>` },
          3: { step:"Stage 3 of 3 · The user does it", title:"You're in control",
               html:`<p>Now you can work independently: paste or upload TXT/MD text, choose Simplify or Summarize, or select a word in the original-text panel and click <strong>Explain selected phrase</strong>.</p>
                     <p>Help is always available through <strong>Tour / Help</strong> or the chat Help button. No AI action is forced or preselected.</p>` }
        };
        function showTour(step) {
            tourState.step = step;
            $("tour").dataset.step = String(step);
            tourState.lastFocus = document.activeElement;
            const stage=stages[step];
            $("tourStep").textContent=stage.step;
            $("tourTitle").textContent=stage.title;
            $("tourDescription").innerHTML=stage.html;
            $("tourNext").textContent= step===1 ? "Next: guided practice" : step===2 ? "Start guided practice" : "Finish tour";
            $("tour").hidden=false;
            $("app").inert=true;
            $("tourNext").focus();
        }
        function closeTour(markComplete=true) {
            $("tour").hidden=true;
            $("app").inert=false;
            if (markComplete) { try { localStorage.setItem("ira_tour_seen_v1", "yes"); } catch {} }
            const focus= tourState.lastFocus;
            if (focus && focus.isConnected) focus.focus();
            else $("openTour").focus();
        }
        $("tourNext").onclick=()=> {
            const step=tourState.step;
            if(step===1) showTour(2);
            else if(step===2){
                closeTour(false);
                tourState.guided=true;
                newText(SAMPLE);
                $("guidedHint").hidden=false;
                $("guidedHint").scrollIntoView({block:"start"});
                const simplify=[...W.querySelectorAll('[data-act="do"]')].find(b=>b.dataset.x==="sim");
                simplify?.focus();
            } else closeTour();
        };
        $("tourSkip").onclick=()=>{tourState.guided=false;$("guidedHint").hidden=true;closeTour();};
        function startTour(){showTour(1);}
        $("openTour").onclick=startTour;
        $("openTourSide").onclick=startTour;
        $("tour").addEventListener("keydown", event => {
            if(event.key==="Escape") { event.preventDefault(); $("tourSkip").click(); }
            if(event.key!=="Tab") return;
            const controls=[$("tourSkip"),$("tourNext")];
            if(event.shiftKey && document.activeElement===controls[0]){event.preventDefault();controls[1].focus();}
            else if(!event.shiftKey && document.activeElement===controls[1]){event.preventDefault();controls[0].focus();}
        });
        document.addEventListener("keydown", event=> {
            if(event.key==="Escape" && $("app").classList.contains("source-open")) setSourceOpen(false);
        });
        welcome();
        // First-visit instructional tour is not an AI request. It can always be replayed.
        let tourSeen = false;
        try { tourSeen = !!localStorage.getItem("ira_tour_seen_v1"); } catch {}
        if (!tourSeen) showTour(1);
