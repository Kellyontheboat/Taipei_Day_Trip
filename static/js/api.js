export async function fetchAttractions(page = 0, keyword = null) {
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
    return await response.json();
  } catch (error) {
    console.error("Error fetching attractions:", error);
    return null;
  }
}

export async function fetchMrtStations() {
  try {
    const response = await fetch('/api/mrts');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching MRT stations:", error);
    return null;
  }
}

export async function fetchAttr(id) {
  try {
    const response = await fetch(`/api/attraction/${id}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching attraction:", error);
    return null;
  }
}


