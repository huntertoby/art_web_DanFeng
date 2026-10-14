// 全站共用：捲動淡入、背景捲動鎖定、照片燈箱

const MODAL_ANIMATION_MS = 300;

function lockScroll() {
    document.body.style.overflow = 'hidden';
}

function unlockScroll() {
    document.body.style.overflow = 'auto';
}

// 依序移除/加入 class，用來切換開關動畫狀態
function swapClasses(el, remove, add) {
    el.classList.remove(...remove);
    el.classList.add(...add);
}

// ---- 捲動淡入 ----
document.addEventListener('DOMContentLoaded', () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.05, rootMargin: '0px 0px -20px 0px' });

    document.querySelectorAll('.fade-in-up').forEach((el) => observer.observe(el));
});

// ---- 照片燈箱：任何帶 data-lightbox="圖片網址" 的元素都可點擊放大 ----
const Lightbox = {
    open(src) {
        const modal = document.getElementById('lightbox');
        const img = document.getElementById('lightboxImg');
        img.src = src;
        modal.classList.remove('hidden');
        setTimeout(() => swapClasses(img, ['scale-95', 'opacity-0'], ['scale-100', 'opacity-100']), 10);
        lockScroll();
    },

    close() {
        const modal = document.getElementById('lightbox');
        const img = document.getElementById('lightboxImg');
        swapClasses(img, ['scale-100', 'opacity-100'], ['scale-95', 'opacity-0']);
        setTimeout(() => {
            modal.classList.add('hidden');
            img.src = '';
            unlockScroll();
        }, MODAL_ANIMATION_MS);
    },

    isOpen() {
        const modal = document.getElementById('lightbox');
        return modal && !modal.classList.contains('hidden');
    },
};

document.addEventListener('click', (event) => {
    const trigger = event.target.closest('[data-lightbox]');
    if (trigger) {
        Lightbox.open(trigger.dataset.lightbox);
    } else if (event.target.closest('[data-lightbox-close]')) {
        Lightbox.close();
    }
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && Lightbox.isOpen()) {
        Lightbox.close();
    }
});
