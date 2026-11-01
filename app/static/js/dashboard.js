// Content Studio Dashboard Logic
let selectedFile = null;
const platforms = ["instagram", "tiktok", "facebook", "threads", "twitter"];

function openConnectModal(plat = null) {
  const modal = document.getElementById("connectModal");
  if (plat) {
    document.getElementById("modalPlatform").value = plat;
    document.getElementById("modalAccountName").value = `@${plat}_creator`;
  }
  modal.classList.remove("hidden");
}

function closeConnectModal() {
  document.getElementById("connectModal").classList.add("hidden");
}

function switchPlatformTab(targetPlat) {
  platforms.forEach(p => {
    const btn = document.getElementById(`tab-btn-${p}`);
    const panel = document.getElementById(`panel-${p}`);
    if (p === targetPlat) {
      btn.className = "platform-tab-btn px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition bg-indigo-600 text-white border border-indigo-500";
      panel.classList.remove("hidden");
    } else {
      btn.className = "platform-tab-btn px-3 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition bg-slate-800/60 text-slate-400 hover:text-white border border-transparent";
      panel.classList.add("hidden");
    }
  });
}

// Media file selection and preview
document.addEventListener("DOMContentLoaded", () => {
  const mediaInput = document.getElementById("mediaInput");
  const dropzone = document.getElementById("dropzone");
  const uploadPrompt = document.getElementById("uploadPrompt");
  const previewContainer = document.getElementById("mediaPreviewContainer");
  const videoPreview = document.getElementById("videoPreview");
  const imagePreview = document.getElementById("imagePreview");
  const fileNameBadge = document.getElementById("fileNameBadge");

  function handleFile(file) {
    if (!file) return;
    selectedFile = file;
    const fileUrl = URL.createObjectURL(file);
    uploadPrompt.classList.add("hidden");
    previewContainer.classList.remove("hidden");
    fileNameBadge.textContent = `${file.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)`;

    if (file.type.startsWith("video/")) {
      videoPreview.src = fileUrl;
      videoPreview.classList.remove("hidden");
      imagePreview.classList.add("hidden");
    } else {
      imagePreview.src = fileUrl;
      imagePreview.classList.remove("hidden");
      videoPreview.classList.add("hidden");
    }
  }

  mediaInput?.addEventListener("change", (e) => handleFile(e.target.files[0]));

  ["dragover", "dragenter"].forEach(evt => {
    dropzone?.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.add("dragover"); });
  });
  ["dragleave", "drop"].forEach(evt => {
    dropzone?.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.remove("dragover"); });
  });
  dropzone?.addEventListener("drop", (e) => {
    if (e.dataTransfer.files?.length) handleFile(e.dataTransfer.files[0]);
  });

  // Twitter char counter
  const xCaption = document.getElementById("caption-twitter");
  const xTags = document.getElementById("hashtags-twitter");
  const xCounter = document.getElementById("xCharCounter");
  function updateXCount() {
    const total = (xCaption.value || document.getElementById("masterCaption").value || "").length + (xTags.value ? xTags.value.length + 2 : 0);
    xCounter.textContent = `${total} / 280`;
    xCounter.className = total > 280 ? "text-[10px] text-rose-400 font-mono font-bold" : "text-[10px] text-slate-400 font-mono";
  }
  xCaption?.addEventListener("input", updateXCount);
  xTags?.addEventListener("input", updateXCount);
});

// One-Click Multi-Platform Publish
async function triggerOneClickPublish() {
  if (!selectedFile) {
    alert("Please select a video reel or image first.");
    return;
  }

  const masterCaption = document.getElementById("masterCaption").value;
  const platformPayloads = {};
  platforms.forEach(p => {
    platformPayloads[p] = {
      caption: document.getElementById(`caption-${p}`)?.value || "",
      hashtags: document.getElementById(`hashtags-${p}`)?.value || ""
    };
  });

  const formData = new FormData();
  formData.append("media_file", selectedFile);
  formData.append("master_caption", masterCaption);
  formData.append("platform_payloads", JSON.stringify(platformPayloads));

  const publishBtn = document.getElementById("publishBtn");
  const publishText = document.getElementById("publishText");
  const publishIcon = document.getElementById("publishIcon");
  const publishSpinner = document.getElementById("publishSpinner");

  publishBtn.disabled = true;
  publishText.textContent = "Publishing to all connected platforms...";
  publishIcon.classList.add("hidden");
  publishSpinner.classList.remove("hidden");

  try {
    const res = await fetch("/posts/publish", { method: "POST", body: formData });
    const data = await res.json();

    if (!data.success) {
      alert("Publish failed: " + (data.error || "Unknown error"));
      return;
    }

    renderPublishResults(data);
  } catch (err) {
    alert("Network or dispatch error: " + err.message);
  } finally {
    publishBtn.disabled = false;
    publishText.textContent = "Publish to All Connected Accounts in One Click";
    publishIcon.classList.remove("hidden");
    publishSpinner.classList.add("hidden");
  }
}

function renderPublishResults(data) {
  const box = document.getElementById("liveResultBox");
  const badges = document.getElementById("liveResultBadges");
  box.classList.remove("hidden");
  badges.innerHTML = "";

  data.results.forEach(r => {
    const badge = document.createElement("div");
    const ok = r.success;
    badge.className = `p-3 rounded-xl border text-xs flex flex-col justify-between ${
      ok ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300" : "bg-rose-500/10 border-rose-500/30 text-rose-300"
    }`;
    badge.innerHTML = `
      <div class="flex items-center justify-between font-semibold capitalize mb-1">
        <span>${r.platform}</span>
        <i class="fa-solid ${ok ? 'fa-check-circle' : 'fa-circle-xmark'}"></i>
      </div>
      <div class="text-[10px] truncate opacity-80">${ok ? (r.platform_post_id || 'Posted') : (r.error || 'Failed')}</div>
    `;
    badges.appendChild(badge);
  });
}

