let map = null;

async function openModal(restaurantId) {
    try {
        const response = await fetch(`/api/restaurants/${restaurantId}`);
        const restaurant = await response.json();
        
        // 모달 내용 업데이트
        document.getElementById('modalRestaurantName').textContent = restaurant.name;
        document.getElementById('modalImage').src = `/static/${restaurant.image_path}`;
        document.getElementById('modalTemperature').textContent = restaurant.temperature;
        document.getElementById('modalHumidity').textContent = restaurant.humidity;
        document.getElementById('modalNoise').textContent = restaurant.noise_level;
        document.getElementById('modalDescription').textContent = restaurant.description;
        
        // 별점 표시
        const ratingDiv = document.getElementById('modalRating');
        ratingDiv.innerHTML = '';
        for (let i = 0; i < Math.floor(restaurant.rating); i++) {
            ratingDiv.innerHTML += '<span class="star filled">★</span>';
        }
        if (restaurant.rating % 1 >= 0.5) {
            ratingDiv.innerHTML += '<span class="star half">★</span>';
        }
        for (let i = Math.ceil(restaurant.rating); i < 5; i++) {
            ratingDiv.innerHTML += '<span class="star empty">☆</span>';
        }
        ratingDiv.innerHTML += `<span class="rating-number">${restaurant.rating.toFixed(1)}</span>`;
        
        // 리뷰 표시
        const reviewsDiv = document.getElementById('modalReviews');
        reviewsDiv.innerHTML = '';
        restaurant.short_reviews.forEach(review => {
            const reviewElement = document.createElement('div');
            reviewElement.className = 'review-item';
            reviewElement.textContent = review;
            reviewsDiv.appendChild(reviewElement);
        });
        
        // 모달 표시
        const modal = document.getElementById('restaurantModal');
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';  // 배경 스크롤 방지
        
        // 지도 표시
        if (map) {
            map.remove();
        }
        
        // 약간의 지연을 주어 모달이 완전히 표시된 후 지도를 초기화
        setTimeout(() => {
            map = L.map('map').setView([restaurant.latitude, restaurant.longitude], 15);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            // 마커 추가
            L.marker([restaurant.latitude, restaurant.longitude])
             .bindPopup(restaurant.name)
             .addTo(map);
             
            // 지도 크기 재조정
            map.invalidateSize();
        }, 100);
        
    } catch (error) {
        console.error('Error:', error);
        alert('정보를 불러오는데 실패했습니다.');
    }
}

function closeModal() {
    const modal = document.getElementById('restaurantModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';  // 배경 스크롤 복구
    if (map) {
        map.remove();
        map = null;
    }
}

// 모달 외부 클릭시 닫기
window.onclick = function(event) {
    const modal = document.getElementById('restaurantModal');
    if (event.target == modal) {
        closeModal();
    }
}

// 모달이 열린 후 지도 크기 조정을 위한 이벤트 리스너
window.addEventListener('resize', () => {
    if (map) {
        map.invalidateSize();
    }
});