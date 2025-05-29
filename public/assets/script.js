async function uploadAudio() {
    const audioInput = document.getElementById('audioInput').files[0];
    const formData = new FormData();
    formData.append('audio', audioInput);

    try {
        const response = await fetch('/api/stt', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        document.getElementById('transcript').textContent = result.transcript || result.error;
    } catch (error) {
        document.getElementById('transcript').textContent = 'Error: ' + error.message;
    }
}

async function sendMessage() {
    const text = document.getElementById('chatInput').value;
    try {
        const response = await fetch('/api/message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const result = await response.json();
        const responseText = result[0]?.text || result.error || 'No response';
        document.getElementById('chatResponse').textContent = responseText;
    } catch (error) {
        document.getElementById('chatResponse').textContent = 'Error: ' + error.message;
    }
}

async function synthesizeSpeech() {
    const text = document.getElementById('ttsInput').value;
    try {
        const response = await fetch('/api/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const audio = document.getElementById('audioOutput');
        audio.src = url;
        audio.play();
    } catch (error) {
        document.getElementById('chatResponse').textContent = 'Error: ' + error.message;
    }
}

async function getCourses() {
    const courseId = document.getElementById('courseInput').value;
    try {
        const response = await fetch(`/courses?id=${encodeURIComponent(courseId)}`);
        const result = await response.json();
        const courseList = document.getElementById('courseList');
        courseList.innerHTML = '';
        if (result.courses) {
            result.courses.forEach(course => {
                const li = document.createElement('li');
                li.textContent = `${course.name}: ${course.description}`;
                courseList.appendChild(li);
            });
        } else {
            courseList.innerHTML = '<li>' + (result.error || 'No courses found') + '</li>';
        }
    } catch (error) {
        document.getElementById('courseList').innerHTML = '<li>Error: ' + error.message + '</li>';
    }
}