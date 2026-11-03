document.addEventListener('DOMContentLoaded', () => {
  const video = document.getElementById('omniLiveVideo') || document.getElementById('homeVideoPlayer');
  if (!video) return;

  const streamSrc = video.getAttribute('src');
  if (!streamSrc) return;

  if (streamSrc.includes('.m3u8') && window.Hls && window.Hls.isSupported()) {
    const hls = new window.Hls({ enableWorker: true, lowLatencyMode: true });
    hls.loadSource(streamSrc);
    hls.attachMedia(video);
    hls.on(window.Hls.Events.MANIFEST_PARSED, () => {
      video.play().catch(() => { video.muted = true; video.play(); });
    });
  } else {
    video.play().catch(() => { video.muted = true; video.play(); });
  }
});
