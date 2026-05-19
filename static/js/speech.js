/*
 * static/js/speech.js
 * Global Jarvis speech utility using the Web Speech API (SpeechSynthesis)
 * - Call JarvisSpeech.init() once on page load (or when user interacts)
 * - Call JarvisSpeech.speak(text) to speak
 * - Works as a UMD module and attaches to window.JarvisSpeech
 */
(function () {
  'use strict';

  const supports = typeof window !== 'undefined' && 'speechSynthesis' in window;
  const synth = supports ? window.speechSynthesis : null;

  let voices = [];
  let preferredVoice = null;

  function loadVoices() {
    if (!supports) return;
    voices = synth.getVoices() || [];
    // Choose a default 'Jarvis-like' voice: prefer en-GB male if available
    preferredVoice =
      voices.find(v => v.lang && v.lang.includes('en-GB') && /male/i.test(v.name)) ||
      voices.find(v => v.lang && v.lang.includes('en-GB')) ||
      voices.find(v => v.lang && v.lang.startsWith('en')) ||
      voices.find(v => v.lang && v.lang.startsWith('pt')) ||
      voices[0] ||
      null;
  }

  function onVoicesChanged() {
    loadVoices();
  }

  function init() {
    if (!supports) return false;
    loadVoices();
    // Some browsers populate voices asynchronously
    synth.addEventListener && synth.addEventListener('voiceschanged', onVoicesChanged);
    return true;
  }

  function isSupported() {
    return supports;
  }

  function getAvailableVoices() {
    return voices.slice();
  }

  function setPreferredVoiceByName(name) {
    if (!supports) return false;
    const v = voices.find(x => x.name === name);
    if (v) {
      preferredVoice = v;
      return true;
    }
    return false;
  }

  function stop() {
    if (!supports) return;
    synth.cancel();
  }

  function speak(text, opts) {
    opts = opts || {};
    if (!supports) return Promise.reject(new Error('Speech synthesis not supported in this browser'));
    if (!text) return Promise.resolve();

    const utter = new SpeechSynthesisUtterance(text);

    // allow overriding language or voice name
    if (opts.lang) utter.lang = opts.lang;
    if (opts.voiceName) {
      const v = voices.find(x => x.name === opts.voiceName);
      if (v) utter.voice = v;
    } else if (preferredVoice) {
      utter.voice = preferredVoice;
    }

    utter.rate = typeof opts.rate === 'number' ? opts.rate : 1; // 0.1 - 10
    utter.pitch = typeof opts.pitch === 'number' ? opts.pitch : 1; // 0 - 2
    utter.volume = typeof opts.volume === 'number' ? opts.volume : 1; // 0 - 1

    return new Promise((resolve) => {
      utter.onend = resolve;
      // speak
      synth.speak(utter);
    });
  }

  // Public API
  const JarvisSpeech = {
    init,
    isSupported,
    speak,
    stop,
    getAvailableVoices,
    setPreferredVoiceByName,
  };

  // Export for module systems and attach to window
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = JarvisSpeech;
  }
  if (typeof define === 'function' && define.amd) {
    define(function () { return JarvisSpeech; });
  }
  if (typeof window !== 'undefined') {
    window.JarvisSpeech = JarvisSpeech;
  }
})();
