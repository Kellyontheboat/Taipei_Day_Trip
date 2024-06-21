import { showLoginModal, updateLoginButton } from './render.js';
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

//! login
export async function validateForm() {
  const signInForm = document.getElementById('signin-form-login');
  if (signInForm) {
    signInForm.addEventListener('submit', async function (event) {
      event.preventDefault(); // Prevent default form submission

      try {

        const token = await validateForm();
        if (token) {
          localStorage.setItem('token', token);
          window.location.href = '/'; // Redirect to homepage
        } else {
          alert('Login failed. Please check your credentials.');
        }
      } catch (error) {
        console.error('Error logging in:', error);
        alert('An error occurred while logging in.');
      }
    });
  }
}

// ! Form submission
// Handle registration form submission
export async function registerformSubmission() {
  const registerForm = document.getElementById('signin-form-register');
  registerForm.addEventListener('submit', async function (event) {
    event.preventDefault();

    const formData = new FormData(registerForm);
    const data = {
      name: formData.get('name'),
      email: formData.get('email'),
      password: formData.get('password')
    };

    try {
      const response = await fetch('/api/user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        showLoginModal();
        const loginSuccessMessage = document.getElementById('login-success-message');
        loginSuccessMessage.style.display = 'block';
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.message}`);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred while registering. Please try again.');
    }
  });
};

export async function loginformSubmission(){
  // Handle login form submission
  const loginForm = document.getElementById('signin-form-login');
  loginForm.addEventListener('submit', async function (event) {
    event.preventDefault();

    const formData = new FormData(loginForm);
    const data = {
      email: formData.get('email'),
      password: formData.get('password')
    };

    try {
      const response = await fetch('/api/user/auth', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        const responseData = await response.json();
        localStorage.setItem('token', responseData.token);
        window.location.href = '/';
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.message}`);
      }
    } catch (error) {
      alert('An error occurred while logging in. Please try again.');
    }
  });
};

export function checkLoginStatus() {
  const token = localStorage.getItem('token');
  if (token) {
    updateLoginButton();
  }
}