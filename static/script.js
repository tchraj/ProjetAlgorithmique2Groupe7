document.getElementById('task-form').addEventListener('submit', function(e) {
    e.preventDefault();

    const tasks = document.getElementById('tasks').value;
    const num_workers = document.getElementById('num_workers').value;
    const algorithm = document.getElementById('algorithm').value;

    fetch('/schedule', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            tasks: tasks,
            num_workers: num_workers,
            algorithm: algorithm
        })
    })
    .then(response => response.json())
    .then(data => {
        const resultsDiv = document.getElementById('results');
        if (data.error) {
            resultsDiv.innerHTML = `<p style="color: red;">Erreur : ${data.error}</p>`;
            return;
        }

        let html = `<h3>Temps total (Makespan): ${data.makespan} secondes</h3>`;
        data.workers.forEach((worker, index) => {
            html += `
                <div>
                    <h4>Commis ${index + 1} (Temps total: ${worker.time}s)</h4>
                    <ul>
                        ${worker.tasks.map(task => `<li>${task[0]}: ${task[1]}s</li>`).join('')}
                    </ul>
                </div>
            `;
        });
        resultsDiv.innerHTML = html;
    })
    .catch(error => {
        console.error('Erreur:', error);
        document.getElementById('results').innerHTML = `<p style="color: red;">Une erreur est survenue.</p>`;
    });
});

