document.addEventListener('DOMContentLoaded', function() {
  // Elements
  const countSlider = document.getElementById('count');
  const countValue = document.getElementById('count-value');
  const discoverySlider = document.getElementById('discovery');
  const discoveryValue = document.getElementById('discovery-value');
  const yearSlider = document.getElementById('year');
  const yearValue = document.getElementById('year-value');
  const popularitySlider = document.getElementById('popularity');
  const popularityValue = document.getElementById('popularity-value');
  const genreChips = document.querySelectorAll('.genre-chip');
  const moodChips = document.querySelectorAll('.mood-chip');
  const generateBtn = document.getElementById('generate-btn');
  const createPlaylistBtn = document.getElementById('create-playlist-btn');
  const loadingContainer = document.getElementById('loading');
  const recommendationsContainer = document.getElementById('recommendations');
  const tracksContainer = document.getElementById('tracks-container');
  const emptyState = document.getElementById('empty-state');
  const errorState = document.getElementById('error-state');
  const errorMessage = document.getElementById('error-message');
  const tryAgainBtn = document.getElementById('try-again-btn');
  
  let currentRecommendations = [];
  
  // Update slider values
  countSlider.addEventListener('input', () => {
    countValue.textContent = countSlider.value;
  });
  
  discoverySlider.addEventListener('input', () => {
    discoveryValue.textContent = discoverySlider.value;
  });
  
  yearSlider.addEventListener('input', () => {
    yearValue.textContent = yearSlider.value;
  });
  
  popularitySlider.addEventListener('input', () => {
    popularityValue.textContent = popularitySlider.value;
  });
  
  // Toggle genre and mood selection
  genreChips.forEach(chip => {
    chip.addEventListener('click', () => {
      chip.classList.toggle('selected');
    });
  });
  
  moodChips.forEach(chip => {
    chip.addEventListener('click', () => {
      chip.classList.toggle('selected');
    });
  });
  
  // Generate recommendations
  generateBtn.addEventListener('click', generateRecommendations);
  
  // Create playlist
  createPlaylistBtn.addEventListener('click', createPlaylist);
  
  // Try again button
  tryAgainBtn.addEventListener('click', () => {
    errorState.classList.add('hidden');
    emptyState.classList.remove('hidden');
  });
  
  function generateRecommendations() {
    // Show loading state
    loadingContainer.classList.remove('hidden');
    recommendationsContainer.classList.add('hidden');
    emptyState.classList.add('hidden');
    errorState.classList.add('hidden');
    
    // Get selected genres and moods
    const selectedGenres = Array.from(document.querySelectorAll('.genre-chip.selected'))
      .map(chip => chip.dataset.genre);
    
    const selectedMoods = Array.from(document.querySelectorAll('.mood-chip.selected'))
      .map(chip => chip.dataset.mood);
    
    // Prepare request data
    const data = {
      count: parseInt(countSlider.value),
      discovery_level: parseInt(discoverySlider.value),
      min_year: parseInt(yearSlider.value),
      max_popularity: parseInt(popularitySlider.value),
      genres: selectedGenres,
      moods: selectedMoods
    };
    
    // Make API request
    fetch('/api/recommendations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    .then(response => {
      if (!response.ok) {
        return response.json().then(data => {
          throw new Error(data.error || 'Failed to generate recommendations');
        });
      }
      return response.json();
    })
    .then(recommendations => {
      // Store recommendations
      currentRecommendations = recommendations;
      
      // Display recommendations
      displayRecommendations(recommendations);
      
      // Hide loading, show recommendations
      loadingContainer.classList.add('hidden');
      recommendationsContainer.classList.remove('hidden');
    })
    .catch(error => {
      console.error('Error:', error);
      
      // Show error state
      loadingContainer.classList.add('hidden');
      errorState.classList.remove('hidden');
      errorMessage.textContent = error.message || 'There was an error generating your recommendations.';
    });
  }
  
  function displayRecommendations(recommendations) {
    // Clear previous recommendations
    tracksContainer.innerHTML = '';
    
    // Create track cards
    recommendations.forEach(track => {
      const trackCard = document.createElement('div');
      trackCard.className = 'track-card';
      trackCard.dataset.uri = track.uri;
      
      const title = document.createElement('h3');
      title.textContent = track.title;
      
      const artist = document.createElement('p');
      artist.textContent = track.artist;
      
      trackCard.appendChild(title);
      trackCard.appendChild(artist);
      
      // Add click handler for preview if available
      if (track.preview_url) {
        trackCard.addEventListener('click', () => {
          window.open(track.preview_url, '_blank');
        });
      }
      
      tracksContainer.appendChild(trackCard);
    });
  }
  
  function createPlaylist() {
    if (currentRecommendations.length === 0) {
      return;
    }
    
    // Show loading
    loadingContainer.classList.remove('hidden');
    
    // Get track URIs
    const trackUris = currentRecommendations.map(track => track.uri);
    
    // Prepare request data
    const data = {
      name: `AI Recommendations ${new Date().toLocaleDateString()}`,
      track_uris: trackUris
    };
    
    // Make API request
    fetch('/api/create-playlist', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
    .then(response => {
      if (!response.ok) {
        return response.json().then(data => {
          throw new Error(data.error || 'Failed to create playlist');
        });
      }
      return response.json();
    })
    .then(playlist => {
      // Hide loading
      loadingContainer.classList.add('hidden');
      
      // Show success message and open playlist
      alert(`Playlist "${playlist.name}" created successfully with ${playlist.tracks} tracks!`);
      window.open(playlist.url, '_blank');
    })
    .catch(error => {
      console.error('Error:', error);
      
      // Hide loading, show error
      loadingContainer.classList.add('hidden');
      alert(`Error creating playlist: ${error.message}`);
    });
  }
});
