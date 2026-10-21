// Native capture adapter for the embedded controller only.
(() => {
  let target = null, pending = null;
  const post = action => window.webkit.messageHandlers.heartPointer.postMessage(action);
  Object.defineProperty(document, 'pointerLockElement', {get: () => target});
  Element.prototype.requestPointerLock = function () {
    if (target || pending) return;
    pending = this;
    post('lock');
  };
  document.exitPointerLock = () => { pending = null; post('unlock'); };
  window.heartPointer = {
    acquired() {
      if (!pending) { post('unlock'); return; }
      target = pending; pending = null;
      document.dispatchEvent(new Event('pointerlockchange'));
    },
    released() {
      target = pending = null;
      document.dispatchEvent(new Event('pointerlockchange'));
      document.dispatchEvent(new KeyboardEvent('keydown', {key:'Escape', bubbles:true}));
    },
    failed() {
      this.released();
      document.dispatchEvent(new Event('pointerlockerror'));
    },
    move(x, y, shift, alt, ctrl, meta) {
      target?.dispatchEvent(new MouseEvent('mousemove', {bubbles:true, movementX:x, movementY:y,
        shiftKey:shift, altKey:alt, ctrlKey:ctrl, metaKey:meta}));
    },
    click() { target?.dispatchEvent(new MouseEvent('click', {bubbles:true})); }
  };
})();
