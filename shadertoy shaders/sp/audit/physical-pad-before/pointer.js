// Native capture adapter for the embedded controller only.
(() => {
  let target = null, pending = null, requestId = 0, sequence = 0;
  const post = (action, id = requestId) => window.webkit.messageHandlers.heartPointer.postMessage({action, id});
  Object.defineProperty(document, 'pointerLockElement', {get: () => target});
  Element.prototype.requestPointerLock = function () {
    if (target || pending) return;
    pending = this; requestId = ++sequence;
    post('lock');
  };
  document.exitPointerLock = () => {
    const active = target || pending;
    post('unlock'); target = pending = null;
    if (active) document.dispatchEvent(new Event('pointerlockchange'));
  };
  window.heartPointer = {
    get pendingTarget() { return pending; },
    acquired(id) {
      if (!pending || id !== requestId) { post('unlock', id); return; }
      target = pending; pending = null;
      document.dispatchEvent(new Event('pointerlockchange'));
    },
    released(id) {
      if (id && id !== requestId) return;
      target = pending = null;
      document.dispatchEvent(new Event('pointerlockchange'));
      document.dispatchEvent(new KeyboardEvent('keydown', {key:'Escape', bubbles:true}));
    },
    failed(id) {
      if (id !== requestId) return;
      this.released(id);
      document.dispatchEvent(new Event('pointerlockerror'));
    },
    move(x, y, shift, alt, ctrl, meta, id = requestId) {
      if (id !== requestId) return;
      target?.dispatchEvent(new MouseEvent('mousemove', {bubbles:true, movementX:x, movementY:y,
        shiftKey:shift, altKey:alt, ctrlKey:ctrl, metaKey:meta}));
    },
    button(down, id = requestId) {
      if (id !== requestId || !target) return;
      // Keep click-to-toggle parameter widgets working while hold gestures get a real release.
      const element = target;
      element.dispatchEvent(new MouseEvent(down ? 'mousedown' : 'mouseup', {bubbles:true, button:0, buttons:down?1:0}));
      if (!down && target === element) element.dispatchEvent(new MouseEvent('click', {bubbles:true}));
    },
    pressure(stage, id = requestId) {
      if (id !== requestId || !target) return;
      target.dispatchEvent(new CustomEvent('heartpressure', {bubbles:true, cancelable:true, detail:{stage}}));
    },
    wheel(x, y, mode, shift, alt, ctrl, meta, id = requestId) {
      if (id !== requestId) return;
      target?.dispatchEvent(new WheelEvent('wheel', {bubbles:true, cancelable:true, deltaX:x, deltaY:y, deltaMode:mode,
        shiftKey:shift, altKey:alt, ctrlKey:ctrl, metaKey:meta}));
    },
    click() { target?.dispatchEvent(new MouseEvent('click', {bubbles:true})); }
  };
})();
