/**
 * Silent Check SSO: post message to parent so keycloak-js can complete check-sso.
 * Loaded only by silent-check-sso.html (same origin). No inline script = CSP script-src 'self' works.
 */
(function () {
  const expectedOrigin = window.location.origin;
  const message = location.href;
  if (window.parent !== window) {
    try {
      window.parent.postMessage(message, expectedOrigin);
    } catch (e) {
      console.error('Failed to post message to parent:', e);
    }
  }
})();
