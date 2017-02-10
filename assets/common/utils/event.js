
/**
 * Adapted from: https://github.com/louisremi/jquery-smartresize#minimalist-standalone-version
 * Executes a given function on resize if no resize events have been fired recently
 * @callback Function to execute on resize
 * @param {number} customDelay Optionally specify delay in ms
*/
export const debouncedResize = (func, customDelay) => {
  // Default to 150ms timeout delay
  const delay = customDelay || 150;
  let timeout;
  window.addEventListener('resize', () => {
    clearTimeout(timeout);
    timeout = setTimeout(func, delay);
  });
};

export { debouncedResize as default };
