// 作品頁：作品詳情彈窗、核心意義彈窗、?art=<id> 直接開啟作品
// 依賴 site.js 的 lockScroll / unlockScroll / swapClasses / MODAL_ANIMATION_MS

const dataEl = document.getElementById('artworkData');
const ARTWORKS = JSON.parse(dataEl.textContent);
const STATIC_ROOT = dataEl.dataset.staticRoot;

const staticUrl = (filename) => encodeURI(STATIC_ROOT + filename);

// 每個彈窗開/關時要切換的 class
const MODAL_STATES = {
    artworkModal: {
        hidden: ['translate-y-full', 'sm:translate-y-8', 'sm:scale-95', 'opacity-0'],
        shown: ['translate-y-0', 'sm:scale-100', 'opacity-100'],
    },
    conclusionModal: {
        hidden: ['scale-90', 'opacity-0'],
        shown: ['scale-100', 'opacity-100'],
    },
};

function openModal(id) {
    const modal = document.getElementById(id);
    const backdrop = modal.querySelector('[data-role="backdrop"]');
    const content = modal.querySelector('[data-role="content"]');

    modal.classList.remove('hidden');
    void modal.offsetWidth; // 強制重繪，讓接下來的 class 變化有動畫

    swapClasses(backdrop, ['opacity-0'], ['opacity-100']);
    swapClasses(content, MODAL_STATES[id].hidden, MODAL_STATES[id].shown);
    lockScroll();
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal.classList.contains('hidden')) return;

    const backdrop = modal.querySelector('[data-role="backdrop"]');
    const content = modal.querySelector('[data-role="content"]');

    swapClasses(backdrop, ['opacity-100'], ['opacity-0']);
    swapClasses(content, MODAL_STATES[id].shown, MODAL_STATES[id].hidden);
    setTimeout(() => {
        modal.classList.add('hidden');
        unlockScroll();
    }, MODAL_ANIMATION_MS);
}

function closeAllModals() {
    const audio = document.getElementById('modalAudio');
    audio.pause();
    audio.currentTime = 0;

    Object.keys(MODAL_STATES).forEach(closeModal);
}

// ---- 作品詳情 ----

function hideAnswer() {
    document.getElementById('answerOverlay').classList.remove('opacity-0', 'pointer-events-none');
    swapClasses(document.getElementById('answerContent'), ['opacity-100', 'blur-none'], ['opacity-0', 'blur-sm']);
}

function revealAnswer() {
    document.getElementById('answerOverlay').classList.add('opacity-0', 'pointer-events-none');
    swapClasses(document.getElementById('answerContent'), ['opacity-0', 'blur-sm'], ['opacity-100', 'blur-none']);
}

// 有值就填入並顯示，沒值就隱藏
function setOptionalText(el, text, display = 'inline-block') {
    const hasText = Boolean(text && text.trim());
    if (hasText) el.textContent = text;
    el.style.display = hasText ? display : 'none';
    return hasText;
}

function fillAudio(art) {
    const container = document.getElementById('modalAudioContainer');
    const audio = document.getElementById('modalAudio');

    if (!art.audio) {
        audio.pause();
        audio.removeAttribute('src');
        container.style.display = 'none';
        return;
    }

    audio.src = staticUrl(art.audio);
    document.getElementById('modalAudioTitle').textContent = art.student_name
        ? `藝術小尖兵(${art.student_name})語音導覽`
        : '學生語音導覽';
    container.style.display = 'block';
}

function openArtwork(id) {
    const art = ARTWORKS[id];
    if (!art) return;

    document.getElementById('modalImg').src = staticUrl(art.img);
    document.getElementById('modalImg').alt = art.title;
    document.getElementById('modalTitle').textContent = art.title;
    document.getElementById('modalArtistYear').textContent = `${art.artist} | ${art.year}`;
    document.getElementById('modalDesc').textContent = art.desc;
    setOptionalText(document.getElementById('modalLocation'), art.location);

    const answerContainer = document.getElementById('modalAnswerContainer');
    if (setOptionalText(document.getElementById('modalAnswer'), art.answer, 'block')) {
        answerContainer.style.display = 'block';
        hideAnswer();
    } else {
        answerContainer.style.display = 'none';
    }

    fillAudio(art);
    openModal('artworkModal');
}

// ---- 事件綁定 ----

document.addEventListener('click', (event) => {
    const artButton = event.target.closest('[data-art-id]');
    if (artButton) return openArtwork(artButton.dataset.artId);
    if (event.target.closest('[data-modal-close]')) return closeAllModals();
    if (event.target.closest('#modalAnswerContainer')) return revealAnswer();
    if (event.target.closest('#conclusionBtn')) return openModal('conclusionModal');
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeAllModals();
});

// 展場 QR Code：artworks.html?art=C-03 直接打開該作品
document.addEventListener('DOMContentLoaded', () => {
    const artId = new URLSearchParams(window.location.search).get('art');
    const button = artId && document.getElementById(`art-btn-${artId}`);
    if (!button) return;

    setTimeout(() => {
        openArtwork(artId);
        button.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 500);
});
