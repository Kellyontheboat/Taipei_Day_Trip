const gridContainerImg = document.querySelector('.grid-container-img');
const loadingSentinel = document.getElementById("loading-sentinel");

//!render attractions
export function renderAttractions(attractions) {
  attractions.forEach(attraction => {
    const gridItem = createGridItem(attraction);
    gridContainerImg.appendChild(gridItem);
  });

  gridContainerImg.appendChild(loadingSentinel);
  updateGridRows();
}

function createGridItem(attraction) {
  const gridItem = document.createElement('div');
  gridItem.classList.add('grid-item-img');
  gridItem.setAttribute('data-id', attraction.id); //using dataset
  const imageDiv = document.createElement('div');
  imageDiv.classList.add('image-div');
  imageDiv.style.backgroundImage = `url('${attraction.images[0]}')`;

  gridItem.addEventListener('click', () => {
    const attractionId = gridItem.dataset.id;
    if (attractionId) {
      window.location.href = `/attraction/${attractionId}`;
    }
  })

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

  spanOfImg.append(mrtstat, cat);
  gridItem.append(imageDiv, title, spanOfImg);

  return gridItem;
}

function updateGridRows() {
  const numItems = document.querySelectorAll('.grid-item-img').length;
  const numColumns = 4;
  const numRows = Math.ceil(numItems / numColumns);
  const rowHeight = window.matchMedia("(max-width: 600px)").matches ? 280 : 242; // 235 + 45, 197 + 45

  gridContainerImg.style.gridTemplateRows = `repeat(${numRows}, ${rowHeight}px)`;
}

export function initStationElements(data, mrtInput, loadMoreAttractions, scrollContainer, updateSearch) {
  const stations = data.data;

  stations.forEach(station => {
    const stationElement = document.createElement('div');
    stationElement.classList.add('station');
    stationElement.textContent = station;
    stationElement.addEventListener('click', () => {
      mrtInput.value = station;
      updateSearch();
    });
    scrollContainer.appendChild(stationElement);
  });
}

//!render attraction
export function renderAttr(attraction) {
  document.getElementById('name').textContent = attraction.name;
  document.getElementById('category-mrt').textContent = `${attraction.category} at ${attraction.mrt}`;
  document.getElementById('description').textContent = attraction.description;
  document.getElementById('address').textContent = attraction.address;
  document.getElementById('direction').textContent = attraction.direction;

  const carouselBox = document.querySelector('.carousel-box');
  const indicatorContainer = document.querySelector('.carousel-indicators');

  function createIndicators(count) {
    indicatorContainer.innerHTML = ''; 
    for (let i = 0; i < count; i++) {
      
      const li = document.createElement('li');
      const label = document.createElement('label');
      label.classList.add('carousel-bullet');
      if (i === 0) {
        label.classList.add('active')
      }
      //label.innerHTML = '•';
      label.setAttribute('for', `carousel-${i}`);
      li.appendChild(label);
      indicatorContainer.appendChild(li);

      // Add event listener to each bullet for direct slide navigation
      label.addEventListener('click', () => {
        setActiveSlide(i);
      });
    }
  }

  attraction.images.forEach((image, index) => {
    const img = document.createElement('img');
    img.classList.add("slides");
    img.src = image;
    img.id = `carousel-${index}`; // Set html id attribute 
    if (index === 0) {
      img.classList.add('active');
    }
    carouselBox.appendChild(img);
  });

  createIndicators(attraction.images.length);

  document.querySelector('.prev').addEventListener('click', () => {
    moveSlide(-1);
  });
  document.querySelector('.next').addEventListener('click', () => {
    moveSlide(1);
  });
};

function moveSlide(direction) {
  const slides = document.querySelectorAll('.slides');
  const activeSlide = document.querySelector('.slides.active');
  let newIndex = [...slides].indexOf(activeSlide) + direction;

  if (newIndex < 0) {
    newIndex = slides.length - 1;
  } else if (newIndex >= slides.length) {
    newIndex = 0;
  }
  setActiveSlide(newIndex);
}
// set active slide and update indicators after clicking
function setActiveSlide(index) {
  const slides = document.querySelectorAll('.slides');
  const indicators = document.querySelectorAll('.carousel-bullet');

  document.querySelector('.slides.active').classList.remove('active');
  slides[index].classList.add('active');
  // operator (?.) ensures this does not throw an error if no active indicator is found
  document.querySelector('.carousel-bullet.active')?.classList.remove('active');
  indicators[index].classList.add('active');
  document.querySelector(`label[for="carousel-${index}"]`).classList.add('active');
}
