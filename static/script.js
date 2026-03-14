const uploadBtn = document.getElementById('upload-btn');
const fileSelector = document.getElementById('file-selector');
const videoPlayer = document.getElementById('main-player');
const imageDisplay = document.getElementById('main-image');

uploadBtn.addEventListener('click', () => fileSelector.click());

fileSelector.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('media', file);

    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();

    if (response.ok) {
        
        if (file.type.startsWith('video/')) {
            imageDisplay.style.display = "none";
            videoPlayer.style.display = "block";
            videoPlayer.src = data.url;
            videoPlayer.load();
            videoPlayer.play();
        } else {
            videoPlayer.style.display = "none";
            imageDisplay.style.display = "block";
            imageDisplay.src = data.url;
        }
        document.getElementById('status-text').innerText = "Upload complete!";
    } else {
        alert("Upload failed: " + data.error);
    }
});