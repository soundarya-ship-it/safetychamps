/**
 * RoadSoS GPS bridge.
 *
 * The GPS button lives in a sandboxed iframe (Streamlit components.html)
 * which is forbidden from calling window.top.location.replace(...) by
 * its sandbox policy. So the iframe posts a {type:'roadsos_gps', lat,
 * lon} message; this script — loaded into the MAIN page — receives it
 * and does the redirect.
 *
 * Loaded via <script src="/app/static/bridge.js"> because Streamlit's
 * st.markdown(unsafe_allow_html=True) strips inline <script> contents
 * when re-rendering (React refuses to execute them).
 */
(function () {
  if (window.__roadsosGpsBridge) {
    console.log("[GPS bridge] already installed, skipping");
    return;
  }
  window.__roadsosGpsBridge = true;
  console.log("[GPS bridge] listener installed on", window.location.href);

  window.addEventListener("message", function (ev) {
    var dt = ev.data;
    if (!dt) return;
    // Accept both shapes for safety
    var lat = dt.lat;
    var lon = dt.lon;
    if (!lat && dt.roadsos_gps) {
      lat = dt.roadsos_gps.lat;
      lon = dt.roadsos_gps.lon;
    }
    if (dt.type !== "roadsos_gps" || lat == null || lon == null) return;

    console.log("[GPS bridge] received", lat, lon, "origin:", ev.origin);
    try {
      var u = new URL(window.location.href);
      u.searchParams.set("lat", String(lat));
      u.searchParams.set("lon", String(lon));
      window.location.replace(u.toString());
    } catch (e) {
      console.warn("[GPS bridge] redirect failed:", e);
    }
  });
})();
