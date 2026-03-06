// Функция для создания снежинок (одна версия)
function createSnow() {
  const snowContainer = document.querySelector('.snow-container');
  if (!snowContainer) return;

  snowContainer.innerHTML = '';
  const snowSymbols = ['❄', '❅', '❆', '＊', '·', '•'];
  const snowCount = window.innerWidth > 768 ? 60 : 30; // Меньше снежинок на мобильных

  for (let i = 0; i < snowCount; i++) {
    const snowflake = document.createElement('div');
    snowflake.className = 'snowflake';
    snowflake.textContent = snowSymbols[Math.floor(Math.random() * snowSymbols.length)];

    const size = Math.random() * 18 + 8;
    const left = Math.random() * 100;
    const duration = 10 + Math.random() * 10;
    const delay = Math.random() * 10;
    const opacity = 0.5 + Math.random() * 0.5;

    snowflake.style.cssText = `
      left: ${left}%;
      font-size: ${size}px;
      opacity: ${opacity};
      animation-duration: ${duration}s;
      animation-delay: ${delay}s;
    `;

    snowContainer.appendChild(snowflake);
  }
}

// Обновление счётчика до Нового года
function updateNewYearCounter() {
  const counter = document.getElementById('newYearCounter');
  if (!counter) return;

  const now = new Date();
  const newYear = new Date(now.getFullYear() + 1, 0, 1);
  const diff = newYear - now;
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  const counterNumber = counter.querySelector('.counter-number');
  if (counterNumber) counterNumber.textContent = days;
}

// Открытие модального окна бронирования
function openBookingModal(cottageName = '') {
  const modal = document.getElementById('bookingModal');
  if (!modal) return;

  if (cottageName) {
    const select = document.getElementById('cottageSelect');
    if (select) select.value = cottageName;
  }

  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

// Закрытие модального окна
function closeModal() {
  const modal = document.getElementById('bookingModal');
  if (!modal) return;

  modal.classList.remove('active');
  document.body.style.overflow = 'auto';
}

// Настройка фильтров для коттеджей
function setupFilters() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const cottageCards = document.querySelectorAll('.cottage-card');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.dataset.filter;
      cottageCards.forEach(card => {
        card.style.display = filter === 'all' || card.dataset.type === filter ? 'block' : 'none';
      });
    });
  });
}

// Настройка мобильного меню (исправленный вариант)
function setupMobileMenu() {
  const menuToggle = document.getElementById('menuToggle');
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.overlay');

  if (!menuToggle || !sidebar) return;

  menuToggle.addEventListener('click', () => {
    sidebar.classList.toggle('active');
    if (overlay) overlay.classList.toggle('active');
    menuToggle.classList.toggle('active');
  });

  // Закрытие меню при клике на оверлей
  if (overlay) {
    overlay.addEventListener('click', () => {
      sidebar.classList.remove('active');
      overlay.classList.remove('active');
      menuToggle.classList.remove('active');
    });
  }
}

// Обработка формы бронирования
function handleBooking(event) {
  event.preventDefault();

  const cottage = document.getElementById('cottageSelect').value;
  const checkin = document.getElementById('checkinDate').value;
  const nights = document.getElementById('nightsCount').value;
  const name = document.getElementById('guestName').value;
  const phone = document.getElementById('guestPhone').value;

  if (!cottage || !checkin || !nights || !name || !phone) {
    alert('Пожалуйста, заполните все поля');
    return;
  }

  const checkinDate = new Date(checkin);
  const formattedDate = checkinDate.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });

  const checkoutDate = new Date(checkinDate);
  checkoutDate.setDate(checkoutDate.getDate() + parseInt(nights));
  const formattedCheckout = checkoutDate.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });

  const message = `🎅 *НОВАЯ ЗАЯВКА НА БРОНИРОВАНИЕ* 🎄
*Тип размещения:* ${cottage}
*Дата заезда:* ${formattedDate}
*Дата выезда:* ${formattedCheckout}
*Количество ночей:* ${nights}
*Имя гостя:* ${name}
*Телефон:* ${phone}
_Заявка отправлена с сайта_`;

  const encodedMessage = encodeURIComponent(message);
  const whatsappNumber = '79506401939';
  const whatsappUrl = `https://wa.me/${whatsappNumber}?text=${encodedMessage}`;

  window.open(whatsappUrl, '_blank');
  alert('🎉 Спасибо! Сейчас откроется WhatsApp для отправки заявки.');
  closeModal();
  event.target.reset();
}

// Инициализация всех функций при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
  createSnow();
  updateNewYearCounter();
  setupFilters();
  setupMobileMenu();

  // Настройка формы бронирования
  const bookingForm = document.querySelector('.booking-form');
  if (bookingForm) bookingForm.addEventListener('submit', handleBooking);

  // Установка минимальной даты в календаре
  const today = new Date().toISOString().split('T')[0];
  const checkinInput = document.getElementById('checkinDate');
  if (checkinInput) checkinInput.min = today;

  // Обновление счётчика каждую минуту
  setInterval(updateNewYearCounter, 60000);

  // Пересоздание снежинок при изменении размера окна
  window.addEventListener('resize', createSnow);

  // Закрытие модального окна при клике вне его или на Escape
  document.addEventListener('click', (e) => {
    const modal = document.getElementById('bookingModal');
    if (modal && e.target === modal) closeModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });

  // Обработка кликов по кнопкам бронирования
  document.querySelectorAll('.cc-book-btn, #bookNow').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const cottage = btn.getAttribute('data-cottage') || '';
      openBookingModal(cottage);
    });
  });
});
