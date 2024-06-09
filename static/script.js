document.addEventListener("DOMContentLoaded", function () {
  const gridContainerImg = document.querySelector('.grid-container-img');
  const loadingSentinel = document.getElementById("loading-sentinel");
  const scrollContainer = document.getElementById('scroll-container');
  const mrtInput = document.getElementById('mrt-input');
  const searchButton = document.getElementById('search-button');


  let currentPage = 0;
  let loading = false;
  let keyword = null;

  async function fetchAttractions(page = 0, keyword = null) {
    const size = 12;
    let url = `/api/attractions?page=${page}&size=${size}`;
    if (keyword) {
      url += `&keyword=${encodeURIComponent(keyword)}`;
    }

    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      return result;
    } catch (error) {
      console.error("Error fetching attractions:", error);
    }
  }

  function renderAttractions(attractions) {
    attractions.forEach(attraction => {
      const gridItem = document.createElement('div');
      gridItem.classList.add('grid-item-img');

      const imageDiv = document.createElement('div');
      imageDiv.classList.add('image-div');
      imageDiv.style.backgroundImage = `url('${attraction.images[0]}')`;

      const title = document.createElement('div');
      title.classList.add('title');
      title.textContent = attraction.name;

      const spanOfImg = document.createElement('div');
      spanOfImg.classList.add('spanOfImg');

      const mrtstat = document.createElement('span');
      mrtstat.classList.add('mrtstat');
      mrtstat.textContent = attraction.mrt;

      const cat = document.createElement('span');
      cat.classList.add('cat');
      cat.textContent = attraction.category;

      spanOfImg.appendChild(mrtstat);
      spanOfImg.appendChild(cat);

      gridItem.appendChild(imageDiv);
      gridItem.appendChild(title); // Append title to gridItem
      gridItem.appendChild(spanOfImg); // Append spanOfImg to gridItem

      gridContainerImg.appendChild(gridItem);
    });

    gridContainerImg.appendChild(loadingSentinel);
  }

  async function loadMoreAttractions() {
    if (loading) return;
    loading = true;

    const result = await fetchAttractions(currentPage, keyword);

    if (result && result.data) {
      renderAttractions(result.data);
    }

    if (result && result.nextPage !== null) {
      currentPage = result.nextPage;
      loading = false;
    } else {
      window.removeEventListener('scroll', handleScroll);
      //appendFooter(); // Add footer when all pages are loaded
    }
  }

  function handleScroll() {
    const sentinelRect = loadingSentinel.getBoundingClientRect();
    const windowHeight = window.innerHeight;

    if (sentinelRect.top <= windowHeight && !loading) {
      loadMoreAttractions();
    }
  }

  // function appendFooter() {
  //   const footer = document.createElement('div');
  //   footer.classList.add('footer');
  //   const footerContent = document.createElement('div')
  //   footerContent.classList.add('footer-text');
  //   footerContent.innerText = 'COPYRIGHT © 2021 台北一日遊';
  //   gridContainerImg.appendChild(footer);
  //   footer.appendChild(footerContent);
  // }

  searchButton.addEventListener('click', function () {
    keyword = mrtInput.value;
    currentPage = 0; // Reset to the first page
    gridContainerImg.innerHTML = ''; // Clear previous results
    loading = false; // Reset loading flag
    window.addEventListener('scroll', handleScroll); // Reattach scroll event listener
    loadMoreAttractions(); // Load attractions based on the search keyword
  });

  loadMoreAttractions();
  window.addEventListener('scroll', handleScroll);

  fetch('/api/mrts')
    .then(response => response.json())
    .then(data => {
      const stations = data.data;
      stations.forEach(station => {
        const stationElement = document.createElement('div');
        
        stationElement.classList.add('station');
        stationElement.textContent = station;
        stationElement.addEventListener('click', () => {
          mrtInput.value = station;
          keyword = station;
          currentPage = 0;
          gridContainerImg.innerHTML = '';
          loading = false;
          window.addEventListener('scroll', handleScroll);
          loadMoreAttractions();
        });
        scrollContainer.appendChild(stationElement);
      });
    });

  document.querySelector('.scroll-button.left').addEventListener('click', () => {
    scrollContainer.scrollBy({ left: -200, behavior: 'smooth' });
  });

  document.querySelector('.scroll-button.right').addEventListener('click', () => {
    scrollContainer.scrollBy({ left: 200, behavior: 'smooth' });
  });
});
