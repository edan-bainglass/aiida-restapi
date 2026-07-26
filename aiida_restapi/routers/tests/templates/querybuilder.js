const out = document.getElementById("out");
const clientError = document.getElementById("clientError");

const API_PREFIX = document.body.dataset.apiPrefix;

async function readResponse(resp) {
  const contentType = resp.headers.get("content-type") || "";
  const text = await resp.text();
  return { contentType, text };
}

function isJsonContentType(contentType) {
  return (
    contentType.includes("application/json") || /\+json\b/i.test(contentType)
  );
}

function setClientError(msg) {
  clientError.textContent = msg ? " " + msg : "";
}

document.getElementById("clearBtn").addEventListener("click", () => {
  out.textContent = "";
  setClientError("");
});

document.getElementById("sendBtn").addEventListener("click", async () => {
  setClientError("");
  const queryText = document.getElementById("query").value;
  const flatCheckbox = document.getElementById("flatCheckbox");
  const fullCheckbox = document.getElementById("fullCheckbox");

  let parsed;
  try {
    parsed = JSON.parse(queryText);
  } catch (e) {
    setClientError("Invalid JSON in query: " + e);
    return;
  }

  let ENDPOINT =
    API_PREFIX +
    "/querybuilder" +
    (flatCheckbox.checked ? "?flat=true" : "") +
    (fullCheckbox.checked
      ? (flatCheckbox.checked ? "&" : "?") + "full=true"
      : "");

  out.textContent = "Sending to: " + ENDPOINT + "\n";

  try {
    const resp = await fetch(ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(parsed),
    });
    const { contentType, text } = await readResponse(resp);
    let bodyText = text;
    let bodyJson = null;
    if (isJsonContentType(contentType)) {
      try {
        bodyJson = JSON.parse(text);
        bodyText = JSON.stringify(bodyJson, null, 2);
      } catch {}
    }
    out.textContent =
      "POST /querybuilder" +
      "\n" +
      "Status: " +
      resp.status +
      " " +
      resp.statusText +
      "\n" +
      "Response Content-Type: " +
      contentType +
      "\n\n" +
      bodyText;
  } catch (err) {
    out.textContent = "Request error: " + err;
  }
});
