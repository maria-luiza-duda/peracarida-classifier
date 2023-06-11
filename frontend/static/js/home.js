document.addEventListener('DOMContentLoaded', function () {
    var carousel = document.querySelector('#myCarousel');
  
    carousel.addEventListener('slide.bs.carousel', function (event) {
      var activeSlide = event.relatedTarget;
      var direction = event.direction;
  
      if (direction === 'left') {
        activeSlide.classList.add('carousel-item-next');
      } else if (direction === 'right') {
        activeSlide.classList.add('carousel-item-prev');
      }
    });
  
    carousel.addEventListener('slid.bs.carousel', function (event) {
      var activeSlide = event.relatedTarget;
      activeSlide.classList.remove('carousel-item-next', 'carousel-item-prev');
    });
  });
  