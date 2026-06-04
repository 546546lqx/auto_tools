(function () {
  'use strict';

  // Shared site-wide helpers only.
  // Keep this file free of page-specific handlers so it won't conflict with
  // page-level inline scripts such as the polygon tool.

  function qs(selector, root) {
    return (root || document).querySelector(selector);
  }

  function qsa(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  window.AppUtils = window.AppUtils || {};
  window.AppUtils.qs = qs;
  window.AppUtils.qsa = qsa;
})();
