import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const csvPath = path.join(__dirname, 'projects.csv');
const slidesPath = path.join(__dirname, 'slides.md');

// 1. Read CSV
const csvData = fs.readFileSync(csvPath, 'utf8');
const lines = csvData.split('\n').filter(line => line.trim() !== '');
const headers = lines[0].split(',');

const projects = lines.slice(1).map(line => {
    const values = line.split(',');
    const p = {};
    headers.forEach((header, i) => {
        p[header.toLowerCase().trim()] = values[i].trim();
    });

    // Type conversion
    p.id = parseInt(p.id);
    p.progress = parseInt(p.progress);

    // Add UI colors
    const colors = {
        'Business Central': '#22d3ee',
        'BC': '#22d3ee',
        'HRMS': '#34d399',
        'CRM': '#fb923c',
        'QuantConnect': '#fbbf24',
        'Quant': '#fbbf24',
        'Custom': '#94a3b8'
    };
    p.color = colors[p.category] || '#a855f7';

    // Shorten category for UI
    if (p.category === 'Business Central') p.category = 'BC';

    return p;
});

// 2. Format as JS Code
const projectsJS = JSON.stringify(projects, null, 2);

// 3. Update slides.md
let slidesContent = fs.readFileSync(slidesPath, 'utf8');

// Use regex to find and replace the projects array in the script setup
const startMarker = 'const projects = ref\\(';
const endMarker = '\\)\n\nconst avgProgress';

const regex = new RegExp(`${startMarker}[\\s\\S]*?${endMarker}`, 'g');
const newContent = `const projects = ref(${projectsJS})\n\nconst avgProgress`;

slidesContent = slidesContent.replace(regex, newContent);

fs.writeFileSync(slidesPath, slidesContent);
console.log('✅ Success: slides.md has been updated with data from projects.csv');
