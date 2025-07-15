

async function captureBodyAsImage() {
    const canvas = await html2canvas(document.body);
    return canvas.toDataURL('image/png');
}


function downloadImage(dataUrl) {
  // Create a temporary link element
  const link = document.createElement('a');
  link.href = dataUrl;
  link.download = 'report.png';

  // Append to DOM, trigger click, then remove
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function downloadPDF() {
    captureBodyAsImage().then(dataUrl => downloadImage(dataUrl));
}
