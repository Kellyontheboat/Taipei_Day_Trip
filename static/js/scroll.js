
export function createScrollHandler(loadMoreAttractions, loading) {
  return function handleScroll() {
    const loadingSentinel = document.getElementById("loading-sentinel");
    const sentinelRect = loadingSentinel.getBoundingClientRect();
    const windowHeight = window.innerHeight;

    if (sentinelRect.top <= windowHeight && !loading) {
      loadMoreAttractions();
    }
  };
}
